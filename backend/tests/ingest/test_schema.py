from datetime import date

from sqlalchemy import inspect, text

from app.core.database import engine

GROCERY_TABLES = {"chains", "stores", "items", "current_prices", "price_history", "ingestion_runs"}


def test_migration_creates_tables():
    tables = set(inspect(engine).get_table_names())
    assert GROCERY_TABLES <= tables
    assert {"users", "sessions", "token_blacklist", "audit_log"} <= tables


def test_price_history_is_partitioned_by_month():
    with engine.connect() as connection:
        partitioned = connection.execute(
            text("SELECT count(*) FROM pg_partitioned_table WHERE partrelid = 'price_history'::regclass")
        ).scalar_one()
    assert partitioned == 1


def test_ensure_month_partition_is_idempotent():
    with engine.begin() as connection:
        connection.execute(text("SELECT ensure_month_partition(:d)"), {"d": date(2026, 10, 1)})
        connection.execute(text("SELECT ensure_month_partition(:d)"), {"d": date(2026, 10, 17)})
        count = connection.execute(
            text("SELECT count(*) FROM pg_class WHERE relname = 'price_history_2026_10'")
        ).scalar_one()
    assert count == 1


def test_item_names_have_a_trigram_index():
    with engine.connect() as connection:
        indexes = connection.execute(text("SELECT indexdef FROM pg_indexes WHERE tablename = 'items'")).scalars().all()
    assert any("gin_trgm_ops" in definition for definition in indexes)
