from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ingest.runner import run_chain

FEEDS = Path(__file__).parent / "fixtures" / "feeds"
NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
ENERGY = "7290107947473"  # Osher Ad store 34: 13.90


@pytest.fixture
def loaded(session):
    run_chain("osher-ad", FEEDS / "osher-ad", now=NOW)
    run_chain("rami-levy", FEEDS / "rami-levy", now=NOW)


def test_search_by_name(client, loaded):
    body = client.get("/api/items/search", params={"q": "אנרג'י"}).json()
    hit = next(i for i in body["items"] if i["barcode"] == ENERGY)
    assert hit["min_price"] == 13.9
    assert hit["store_count"] == 1


def test_search_by_barcode(client, loaded):
    items = client.get("/api/items/search", params={"q": ENERGY}).json()["items"]
    assert [i["barcode"] for i in items] == [ENERGY]


def test_search_needs_two_characters(client):
    assert client.get("/api/items/search", params={"q": "a"}).status_code == 422


def test_item_prices_per_store(client, loaded):
    body = client.get(f"/api/items/{ENERGY}").json()
    assert body["name"] == "מאגדת אנרג'י תחתית פ"
    assert body["prices"][0] == {
        "chain": "אושר עד", "store": body["prices"][0]["store"], "city": body["prices"][0]["city"],
        "price": 13.9, "unit_price": 0.07, "price_updated_at": "2026-05-10T11:36:13Z",
    }


def test_unknown_item_is_404(client, loaded):
    assert client.get("/api/items/0000").status_code == 404


def test_basket_ranks_stores_and_marks_missing(client, loaded):
    body = client.post("/api/basket/compare", json={"barcodes": [ENERGY, "nope"]}).json()
    best = body["stores"][0]
    assert best["total"] == 13.9
    assert best["missing"] == ["nope"]
    assert best["found"] == 1


def test_basket_filters_by_city(client, loaded):
    body = client.post("/api/basket/compare", json={"barcodes": [ENERGY], "city": "עיר שאין"}).json()
    assert body["stores"] == []


def test_cities_list(client, loaded):
    cities = client.get("/api/cities").json()
    assert "ירושלים" in cities


def test_ingestion_status(client, loaded):
    rows = {r["chain"]: r for r in client.get("/api/status").json()}
    assert rows["אושר עד"]["status"] == "success"
    assert rows["אושר עד"]["items"] == 200
