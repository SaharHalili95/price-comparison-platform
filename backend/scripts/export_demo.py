"""
Writes frontend/public/demo-snapshot.json: a small, real slice of the database for the static GitHub Pages demo.

Keeps the products sold by the most stores (so comparisons are meaningful) with their prices, plus the latest
ingestion run per chain. Run after an ingestion:  cd backend && python scripts/export_demo.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "demo-snapshot.json"
ITEMS = 300
STORES_PER_CHAIN = 5


def main() -> None:
    with SessionLocal() as db:
        keep = {
            (chain, store)
            for chain, store in db.execute(
                text(
                    "SELECT chain, store FROM (SELECT ch.name AS chain, s.name AS store, "
                    "row_number() OVER (PARTITION BY s.chain_id ORDER BY s.id) AS n "
                    "FROM stores s JOIN chains ch ON ch.id = s.chain_id "
                    "WHERE EXISTS (SELECT 1 FROM current_prices c WHERE c.store_pk = s.id)) t WHERE n <= :k"
                ),
                {"k": STORES_PER_CHAIN},
            )
        }
        barcodes = db.execute(
            text(
                "SELECT c.barcode FROM current_prices c JOIN stores s ON s.id = c.store_pk "
                "GROUP BY c.barcode HAVING count(DISTINCT s.chain_id) >= 2 "
                "ORDER BY count(*) DESC LIMIT :n"
            ),
            {"n": ITEMS},
        ).scalars().all()
    with TestClient(app) as client:
        items = []
        for barcode in barcodes:
            item = client.get(f"/api/items/{barcode}").json()
            item["prices"] = [p for p in item["prices"] if (p["chain"], p["store"]) in keep]
            if len({p["chain"] for p in item["prices"]}) >= 2:
                items.append(item)
        snapshot = {"items": items, "cities": client.get("/api/cities").json(), "status": client.get("/api/status").json()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT}: {len(items)} items, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
