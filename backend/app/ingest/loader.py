"""
Writes parsed records to PostgreSQL.

Each batch is COPYed into a temporary staging table, and two set-based statements do the rest: price_history gets
a row only where the price is new or differs from the current one, and current_prices is upserted. Re-loading the
same file therefore adds nothing.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from itertools import islice

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingest.records import PriceRecord, StoreRecord

BATCH_SIZE = 2_000
MIN_BARCODE_LENGTH = 8


@dataclass
class LoadStats:
    items: int = 0
    price_changes: int = 0
    unknown_stores: int = 0


def item_key(code: str, chain_id: str) -> str:
    """Real barcodes are shared across chains; short internal codes (Rami Levy's tomatoes are '100') are not."""
    return code if code.isdigit() and len(code) >= MIN_BARCODE_LENGTH else f"{chain_id}:{code}"


def ensure_chain(session: Session, *, chain_id: str, slug: str, name: str, portal: str) -> None:
    session.execute(
        text(
            "INSERT INTO chains (id, slug, name, portal) VALUES (:id, :slug, :name, :portal) "
            "ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, name = EXCLUDED.name, portal = EXCLUDED.portal"
        ),
        {"id": chain_id, "slug": slug, "name": name, "portal": portal},
    )
    session.commit()


def load_stores(session: Session, records: Iterable[StoreRecord]) -> int:
    rows = [r.__dict__ for r in records]
    if rows:
        session.execute(
            text(
                "INSERT INTO stores (chain_id, sub_chain_id, store_id, name, address, city) "
                "VALUES (:chain_id, :sub_chain_id, :store_id, :name, :address, :city) "
                "ON CONFLICT (chain_id, sub_chain_id, store_id) "
                "DO UPDATE SET name = EXCLUDED.name, address = EXCLUDED.address, city = EXCLUDED.city"
            ),
            rows,
        )
    session.commit()
    return len(rows)


def _batches(records: Iterable[PriceRecord]) -> Iterator[list[PriceRecord]]:
    iterator = iter(records)
    while batch := list(islice(iterator, BATCH_SIZE)):
        yield batch


_STAGING = """
CREATE TEMP TABLE IF NOT EXISTS price_staging (
    seq integer, chain_id text, sub_chain_id text, store_id text, barcode text, name text, manufacturer text,
    unit_of_measure text, quantity numeric, is_weighted boolean, price numeric, unit_price numeric,
    price_updated_at timestamp
)
"""

# The last row wins when a file lists the same item twice for a store. Stores are matched on chain and store number;
# the sub-chain only breaks ties, because some chains (Yohananof) write 000 in price files and 001 in the store list.
_STORE_MATCH = """
JOIN LATERAL (
    SELECT st.id FROM stores st
    WHERE st.chain_id = p.chain_id AND st.store_id = p.store_id
    ORDER BY (st.sub_chain_id = p.sub_chain_id) DESC, st.id
    LIMIT 1
) st ON true
"""

_LATEST = f"""
latest AS (
    SELECT DISTINCT ON (st.id, p.barcode) st.id AS store_pk, p.*
    FROM price_staging p
    {_STORE_MATCH}
    ORDER BY st.id, p.barcode, p.seq DESC
)
"""


def load_prices(session: Session, records: Iterable[PriceRecord], observed_at: datetime) -> LoadStats:
    stats = LoadStats()
    session.execute(text("SELECT ensure_month_partition(CAST(:day AS date))"), {"day": observed_at.date()})
    session.execute(text(_STAGING))
    for batch in _batches(records):
        session.execute(text("TRUNCATE price_staging"))
        _copy(session, batch)
        stats.unknown_stores += session.execute(
            text(
                "SELECT count(*) FROM price_staging p WHERE NOT EXISTS "
                "(SELECT 1 FROM stores st WHERE st.chain_id = p.chain_id AND st.store_id = p.store_id)"
            )
        ).scalar_one()
        session.execute(
            text(
                f"WITH {_LATEST} INSERT INTO items (barcode, name, manufacturer, unit_of_measure, quantity, is_weighted) "
                "SELECT DISTINCT ON (barcode) barcode, name, manufacturer, unit_of_measure, quantity, is_weighted "
                "FROM latest ORDER BY barcode, seq DESC "
                "ON CONFLICT (barcode) DO UPDATE SET name = EXCLUDED.name, manufacturer = EXCLUDED.manufacturer, "
                "unit_of_measure = EXCLUDED.unit_of_measure, quantity = EXCLUDED.quantity, is_weighted = EXCLUDED.is_weighted"
            )
        )
        stats.price_changes += session.execute(
            text(
                f"WITH {_LATEST} INSERT INTO price_history (store_pk, barcode, price, observed_at) "
                "SELECT l.store_pk, l.barcode, l.price, :observed_at FROM latest l "
                "LEFT JOIN current_prices c ON c.store_pk = l.store_pk AND c.barcode = l.barcode "
                "WHERE c.price IS DISTINCT FROM l.price"
            ),
            {"observed_at": observed_at},
        ).rowcount
        stats.items += session.execute(
            text(
                f"WITH {_LATEST} INSERT INTO current_prices (store_pk, barcode, price, unit_price, price_updated_at, observed_at) "
                "SELECT store_pk, barcode, price, unit_price, price_updated_at, :observed_at FROM latest "
                "ON CONFLICT (store_pk, barcode) DO UPDATE SET price = EXCLUDED.price, unit_price = EXCLUDED.unit_price, "
                "price_updated_at = EXCLUDED.price_updated_at, observed_at = EXCLUDED.observed_at"
            ),
            {"observed_at": observed_at},
        ).rowcount
        session.commit()
    return stats


def _copy(session: Session, batch: list[PriceRecord]) -> None:
    connection = session.connection().connection.driver_connection
    columns = (
        "seq, chain_id, sub_chain_id, store_id, barcode, name, manufacturer, unit_of_measure, quantity, "
        "is_weighted, price, unit_price, price_updated_at"
    )
    with connection.cursor() as cursor, cursor.copy(f"COPY price_staging ({columns}) FROM STDIN") as copy:
        for seq, r in enumerate(batch):
            copy.write_row((
                seq, r.chain_id, r.sub_chain_id, r.store_id, item_key(r.barcode, r.chain_id), r.name, r.manufacturer,
                r.unit_of_measure, r.quantity, r.is_weighted, r.price, r.unit_price, r.price_updated_at,
            ))
