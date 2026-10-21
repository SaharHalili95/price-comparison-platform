"""take a lock before creating a price_history partition

Revision ID: 0003
Revises: 0002

Ingestion jobs for different chains run in parallel; two of them reaching a new month together both saw no partition,
and one failed with "relation already exists".
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ensure_month_partition(day date) RETURNS void LANGUAGE plpgsql AS $$
        DECLARE
            start_date date := date_trunc('month', day)::date;
            name text := format('price_history_%s', to_char(start_date, 'YYYY_MM'));
        BEGIN
            IF to_regclass(name) IS NOT NULL THEN
                RETURN;
            END IF;
            -- The lock makes jobs take turns; the handler covers the job that waited and then found the partition
            -- created by another one (its catalog snapshot can predate that commit).
            PERFORM pg_advisory_xact_lock(hashtext('price_history_partitions'));
            BEGIN
                EXECUTE format(
                    'CREATE TABLE %I PARTITION OF price_history FOR VALUES FROM (%L) TO (%L)',
                    name, start_date, (start_date + interval '1 month')::date
                );
            EXCEPTION WHEN duplicate_table OR unique_violation THEN
                NULL;
            END;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ensure_month_partition(day date) RETURNS void LANGUAGE plpgsql AS $$
        DECLARE
            start_date date := date_trunc('month', day)::date;
            name text := format('price_history_%s', to_char(start_date, 'YYYY_MM'));
        BEGIN
            IF to_regclass(name) IS NULL THEN
                EXECUTE format(
                    'CREATE TABLE %I PARTITION OF price_history FOR VALUES FROM (%L) TO (%L)',
                    name, start_date, (start_date + interval '1 month')::date
                );
            END IF;
        END $$;
        """
    )
