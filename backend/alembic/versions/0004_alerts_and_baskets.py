"""price alerts and saved baskets

Revision ID: 0004
Revises: 0003
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE price_alerts (
            id serial PRIMARY KEY,
            user_id integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            barcode varchar(32) NOT NULL REFERENCES items(barcode),
            target_price numeric(10, 2),
            created_at timestamptz NOT NULL DEFAULT now(),
            last_notified_at timestamptz,
            UNIQUE (user_id, barcode)
        );
        CREATE INDEX ix_price_alerts_barcode ON price_alerts (barcode);
        CREATE TABLE saved_baskets (
            user_id integer PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            barcodes jsonb NOT NULL DEFAULT '[]'::jsonb,
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS saved_baskets, price_alerts")
