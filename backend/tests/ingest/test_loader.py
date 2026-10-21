import time
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text

from app.ingest.loader import ensure_chain, item_key, load_prices, load_stores
from app.ingest.parsers import parse_prices, parse_stores
from app.ingest.records import PriceRecord, StoreRecord

FEEDS = Path(__file__).parent.parent / "fixtures" / "feeds" / "osher-ad"
OSHER = "7290103152017"
OCT_21 = datetime(2026, 10, 21, 3, 0, tzinfo=timezone.utc)
OCT_22 = datetime(2026, 10, 22, 3, 0, tzinfo=timezone.utc)


def osher_records() -> list[PriceRecord]:
    with (FEEDS / "PriceFull7290103152017-001-034-20261021-110502.gz").open("rb") as source:
        return list(parse_prices(source))


def load_osher_stores(session) -> None:
    ensure_chain(session, chain_id=OSHER, slug="osher-ad", name="אושר עד", portal="cerberus")
    with (FEEDS / "Stores7290103152017-000-20261021-080500.xml").open("rb") as source:
        load_stores(session, parse_stores(source))


def count(session, table: str) -> int:
    return session.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


def price_of(session, barcode: str) -> Decimal:
    return session.execute(text("SELECT price FROM current_prices WHERE barcode = :b"), {"b": barcode}).scalar_one()


def test_stores_are_upserted(session):
    load_osher_stores(session)
    load_osher_stores(session)
    assert count(session, "stores") == 24


def test_first_load_records_history(session):
    load_osher_stores(session)
    stats = load_prices(session, osher_records(), OCT_21)
    assert stats.items == 200
    assert stats.price_changes == 200
    assert count(session, "price_history") == 200
    assert count(session, "current_prices") == 200


def test_reloading_the_same_file_adds_nothing(session):
    load_osher_stores(session)
    load_prices(session, osher_records(), OCT_21)
    stats = load_prices(session, osher_records(), OCT_22)
    assert stats.price_changes == 0
    assert count(session, "price_history") == 200


def test_changed_price_adds_one_row(session):
    load_osher_stores(session)
    records = osher_records()
    load_prices(session, records, OCT_21)
    changed = [replace(r, price=Decimal("11.90")) if r.barcode == "7290107947473" else r for r in records]
    stats = load_prices(session, changed, OCT_22)
    assert stats.price_changes == 1
    assert price_of(session, "7290107947473") == Decimal("11.90")
    history = session.execute(
        text("SELECT price FROM price_history WHERE barcode = '7290107947473' ORDER BY observed_at")
    ).scalars().all()
    assert history == [Decimal("13.90"), Decimal("11.90")]


def test_history_goes_into_the_month_partition(session):
    load_osher_stores(session)
    load_prices(session, osher_records(), OCT_21)
    assert count(session, "price_history_2026_10") == 200
    assert count(session, "price_history_default") == 0


def test_unknown_store_is_counted_not_loaded(session):
    load_osher_stores(session)
    records = [replace(r, store_id="999") for r in osher_records()[:5]]
    stats = load_prices(session, records, OCT_21)
    assert stats.unknown_stores == 5
    assert stats.items == 0
    assert count(session, "current_prices") == 0


def test_internal_codes_are_scoped_to_the_chain():
    assert item_key("7290107947473", OSHER) == "7290107947473"
    assert item_key("100", OSHER) == f"{OSHER}:100"
    assert item_key("0012345", OSHER) == f"{OSHER}:0012345"
    # A real EAN-13 can start with 0 (US products) and is still shared across chains.
    assert item_key("0012345678905", OSHER) == "0012345678905"


def test_duplicate_item_in_one_file_keeps_the_last(session):
    load_osher_stores(session)
    first = osher_records()[0]
    load_prices(session, [first, replace(first, price=Decimal("1.00"))], OCT_21)
    assert price_of(session, first.barcode) == Decimal("1.00")


def test_full_sample_loads_quickly(session):
    load_osher_stores(session)
    records = osher_records() * 30
    stores = [StoreRecord(OSHER, "1", str(n), f"s{n}", "", "") for n in range(100, 130)]
    load_stores(session, stores)
    spread = [replace(r, store_id=str(100 + i // 200)) for i, r in enumerate(records)]
    start = time.perf_counter()
    stats = load_prices(session, spread, OCT_21)
    assert stats.items == 6000
    assert time.perf_counter() - start < 5
