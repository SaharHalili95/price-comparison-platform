from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/api", tags=["prices"])


def _money(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"


@router.get("/items/search")
def search_items(q: str = Query(min_length=2, max_length=80), limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    """Barcode exact match, else Hebrew name match ranked by trigram similarity."""
    rows = db.execute(
        text(
            """
            SELECT i.barcode, i.name, i.manufacturer, min(c.price) AS min_price, max(c.price) AS max_price,
                   count(c.store_pk) AS store_count
            FROM items i JOIN current_prices c ON c.barcode = i.barcode
            WHERE i.barcode = :q OR i.name ILIKE '%' || :q || '%'
            GROUP BY i.barcode
            ORDER BY (i.barcode = :q) DESC, similarity(i.name, :q) DESC, count(c.store_pk) DESC
            LIMIT :limit
            """
        ),
        {"q": q.strip(), "limit": limit},
    ).mappings()
    return {"query": q, "items": [{**r, "min_price": _money(r["min_price"]), "max_price": _money(r["max_price"])} for r in rows]}


@router.get("/items/{barcode}")
def item_prices(barcode: str, city: str | None = None, db: Session = Depends(get_db)):
    item = db.execute(text("SELECT barcode, name, manufacturer, unit_of_measure FROM items WHERE barcode = :b"), {"b": barcode}).mappings().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    prices = db.execute(
        text(
            """
            SELECT ch.name AS chain, s.name AS store, s.city, c.price, c.unit_price, c.price_updated_at
            FROM current_prices c JOIN stores s ON s.id = c.store_pk JOIN chains ch ON ch.id = s.chain_id
            WHERE c.barcode = :b AND (CAST(:city AS text) IS NULL OR s.city = :city)
            ORDER BY c.price, ch.name, s.name
            """
        ),
        {"b": barcode, "city": city},
    ).mappings()
    return {
        **item,
        "prices": [
            {**p, "price": _money(p["price"]), "unit_price": _money(p["unit_price"]), "price_updated_at": _utc(p["price_updated_at"])}
            for p in prices
        ],
    }


class BasketRequest(BaseModel):
    barcodes: list[str] = Field(min_length=1, max_length=100)
    city: str | None = None


@router.post("/basket/compare")
def compare_basket(basket: BasketRequest, db: Session = Depends(get_db)):
    """Total per store for the items it has, most complete basket first, then cheapest."""
    wanted = list(dict.fromkeys(basket.barcodes))
    rows = db.execute(
        text(
            """
            SELECT s.id, ch.name AS chain, s.name AS store, s.city, sum(c.price) AS total,
                   array_agg(c.barcode) AS found
            FROM current_prices c JOIN stores s ON s.id = c.store_pk JOIN chains ch ON ch.id = s.chain_id
            WHERE c.barcode = ANY(:barcodes) AND (CAST(:city AS text) IS NULL OR s.city = :city)
            GROUP BY s.id, ch.name
            ORDER BY count(*) DESC, sum(c.price)
            LIMIT 30
            """
        ),
        {"barcodes": wanted, "city": basket.city},
    ).mappings()
    stores = [
        {
            "chain": r["chain"], "store": r["store"], "city": r["city"], "total": _money(r["total"]),
            "found": len(r["found"]), "missing": [b for b in wanted if b not in r["found"]],
        }
        for r in rows
    ]
    return {"requested": len(wanted), "stores": stores}


@router.get("/cities")
def cities(db: Session = Depends(get_db)):
    return db.execute(text("SELECT DISTINCT city FROM stores WHERE city <> '' ORDER BY city")).scalars().all()


@router.get("/status")
def ingestion_status(db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT DISTINCT ON (r.chain_id) ch.name AS chain, r.status, r.started_at, r.finished_at, r.newest_file_at,
                   r.files_ok, r.files_failed, r.items, r.price_changes
            FROM ingestion_runs r JOIN chains ch ON ch.id = r.chain_id
            ORDER BY r.chain_id, r.started_at DESC
            """
        )
    ).mappings()
    return [{**r, "started_at": _utc(r["started_at"]), "finished_at": _utc(r["finished_at"]), "newest_file_at": _utc(r["newest_file_at"])} for r in rows]
