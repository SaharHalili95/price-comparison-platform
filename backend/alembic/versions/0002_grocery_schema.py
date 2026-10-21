"""grocery schema with monthly-partitioned price history

Revision ID: 0002
Revises: 0001
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        CREATE TABLE chains (
            id varchar(13) PRIMARY KEY,
            slug varchar(40) NOT NULL UNIQUE,
            name text NOT NULL,
            portal varchar(20) NOT NULL
        );
        CREATE TABLE stores (
            id serial PRIMARY KEY,
            chain_id varchar(13) NOT NULL REFERENCES chains(id),
            sub_chain_id varchar(10) NOT NULL,
            store_id varchar(10) NOT NULL,
            name text NOT NULL,
            address text NOT NULL DEFAULT '',
            city text NOT NULL DEFAULT '',
            UNIQUE (chain_id, sub_chain_id, store_id)
        );
        CREATE INDEX ix_stores_city ON stores (city);
        CREATE TABLE items (
            barcode varchar(32) PRIMARY KEY,
            name text NOT NULL,
            manufacturer text NOT NULL DEFAULT '',
            unit_of_measure text NOT NULL DEFAULT '',
            quantity numeric(12, 3),
            is_weighted boolean NOT NULL DEFAULT false
        );
        CREATE INDEX ix_items_name_trgm ON items USING gin (name gin_trgm_ops);
        CREATE TABLE current_prices (
            store_pk integer NOT NULL REFERENCES stores(id),
            barcode varchar(32) NOT NULL REFERENCES items(barcode),
            price numeric(10, 2) NOT NULL,
            unit_price numeric(10, 2),
            price_updated_at timestamptz,
            observed_at timestamptz NOT NULL,
            PRIMARY KEY (store_pk, barcode)
        );
        CREATE INDEX ix_current_prices_barcode ON current_prices (barcode);
        -- A row only when a store's price for an item changes; one partition per month keeps old months cheap to drop.
        CREATE TABLE price_history (
            store_pk integer NOT NULL,
            barcode varchar(32) NOT NULL,
            price numeric(10, 2) NOT NULL,
            observed_at timestamptz NOT NULL
        ) PARTITION BY RANGE (observed_at);
        CREATE TABLE price_history_default PARTITION OF price_history DEFAULT;
        CREATE INDEX ix_price_history_item ON price_history (barcode, store_pk, observed_at);
        CREATE TABLE ingestion_runs (
            id serial PRIMARY KEY,
            chain_id varchar(13) NOT NULL REFERENCES chains(id),
            started_at timestamptz NOT NULL,
            finished_at timestamptz,
            status varchar(10) NOT NULL CHECK (status IN ('running', 'success', 'partial', 'stale', 'failed')),
            newest_file_at timestamptz,
            files_ok integer NOT NULL DEFAULT 0,
            files_failed integer NOT NULL DEFAULT 0,
            items integer NOT NULL DEFAULT 0,
            price_changes integer NOT NULL DEFAULT 0,
            errors jsonb NOT NULL DEFAULT '[]'::jsonb
        );
        CREATE INDEX ix_ingestion_runs_chain_id ON ingestion_runs (chain_id);
        """
    )
    op.execute(
        """
        CREATE FUNCTION ensure_month_partition(day date) RETURNS void LANGUAGE plpgsql AS $$
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


def downgrade() -> None:
    op.execute(
        """
        DROP FUNCTION IF EXISTS ensure_month_partition(date);
        DROP TABLE IF EXISTS ingestion_runs, price_history, current_prices, items, stores, chains CASCADE;
        """
    )
