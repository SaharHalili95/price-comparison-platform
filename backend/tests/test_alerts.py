from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text

from app.alerts.events import AlertEvent, find_triggered_alerts, mark_notified
from app.alerts.notifier import handle_event
from app.ingest.loader import load_prices
from app.ingest.parsers import parse_prices
from app.ingest.runner import run_chain

FEEDS = Path(__file__).parent / "fixtures" / "feeds"
NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
ENERGY = "7290107947473"  # 13.90 at Osher Ad store 34


def google_login(client, monkeypatch, email="noa@example.com", verified=True):
    import app.api.auth_routes as routes

    monkeypatch.setattr(routes.settings, "GOOGLE_CLIENT_ID", "test-client.apps.googleusercontent.com")
    monkeypatch.setattr(routes, "verify_google_token", lambda token, client_id: {"email": email, "email_verified": verified, "name": "Noa"})
    return client.post("/api/auth/google", json={"credential": "fake-id-token"})


@pytest.fixture
def user_headers(client, monkeypatch, session):
    response = google_login(client, monkeypatch)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def loaded(session):
    run_chain("osher-ad", FEEDS / "osher-ad", now=NOW)


def test_google_sign_in_creates_one_user(client, monkeypatch, session):
    assert google_login(client, monkeypatch).status_code == 200
    assert google_login(client, monkeypatch).status_code == 200
    assert session.execute(text("SELECT count(*) FROM users WHERE email = 'noa@example.com'")).scalar_one() == 1


def test_unverified_google_email_is_rejected(client, monkeypatch, session):
    assert google_login(client, monkeypatch, verified=False).status_code == 401


def test_google_sign_in_needs_configuration(client, monkeypatch):
    import app.api.auth_routes as routes

    monkeypatch.setattr(routes.settings, "GOOGLE_CLIENT_ID", "")
    assert client.post("/api/auth/google", json={"credential": "x"}).status_code == 503


def test_alerts_need_sign_in(client):
    assert client.get("/api/alerts").status_code in (401, 403)


def test_create_list_and_delete_alert(client, user_headers, loaded):
    created = client.post("/api/alerts", json={"barcode": ENERGY, "target_price": 12.5}, headers=user_headers)
    assert created.status_code == 201
    alerts = client.get("/api/alerts", headers=user_headers).json()
    assert [(a["barcode"], a["target_price"], a["current_min_price"]) for a in alerts] == [(ENERGY, 12.5, 13.9)]
    assert client.delete(f"/api/alerts/{alerts[0]['id']}", headers=user_headers).status_code == 204
    assert client.get("/api/alerts", headers=user_headers).json() == []


def test_alert_for_unknown_item_is_404(client, user_headers, loaded):
    assert client.post("/api/alerts", json={"barcode": "nope"}, headers=user_headers).status_code == 404


def test_saved_basket_round_trip(client, user_headers):
    assert client.put("/api/basket", json={"barcodes": [ENERGY, "b"]}, headers=user_headers).status_code == 200
    assert client.get("/api/basket", headers=user_headers).json() == {"barcodes": [ENERGY, "b"]}


def drop_price(session, to: str, when: datetime) -> None:
    with (FEEDS / "osher-ad" / "PriceFull7290103152017-001-034-20261021-110502.gz").open("rb") as source:
        records = [replace(r, price=Decimal(to)) if r.barcode == ENERGY else r for r in parse_prices(source)]
    load_prices(session, records, when)


def test_drop_to_target_triggers_once(client, user_headers, loaded, session):
    client.post("/api/alerts", json={"barcode": ENERGY, "target_price": 12.5}, headers=user_headers)
    later = NOW + timedelta(days=1)
    drop_price(session, "12.00", later)
    events = find_triggered_alerts(session, later)
    assert [(e.email, e.barcode, e.price, e.previous_price) for e in events] == [("noa@example.com", ENERGY, 12.0, 13.9)]
    mark_notified(session, [e.alert_id for e in events], later)
    assert find_triggered_alerts(session, later) == []


def test_drop_above_target_does_not_trigger(client, user_headers, loaded, session):
    client.post("/api/alerts", json={"barcode": ENERGY, "target_price": 10}, headers=user_headers)
    later = NOW + timedelta(days=1)
    drop_price(session, "12.00", later)
    assert find_triggered_alerts(session, later) == []


def test_any_drop_triggers_without_target(client, user_headers, loaded, session):
    client.post("/api/alerts", json={"barcode": ENERGY}, headers=user_headers)
    later = NOW + timedelta(days=1)
    drop_price(session, "13.50", later)
    assert len(find_triggered_alerts(session, later)) == 1


def test_notifier_sends_a_hebrew_email():
    sent: list[tuple[str, str, str]] = []
    event = AlertEvent(alert_id=1, email="noa@example.com", barcode=ENERGY, name="מאגדת אנרג'י", price=12.0, previous_price=13.9, chain="אושר עד", store="נתניה")
    handle_event(event, lambda to, subject, body: sent.append((to, subject, body)))
    to, subject, body = sent[0]
    assert to == "noa@example.com"
    assert "מאגדת אנרג'י" in subject
    assert "12.00" in body and "13.90" in body and "אושר עד" in body


def test_event_round_trips_as_json():
    event = AlertEvent(alert_id=1, email="a@b.c", barcode="1", name="x", price=1.0, previous_price=2.0, chain="c", store="s")
    assert AlertEvent.from_json(event.to_json()) == event


def lower_fixture_price(directory: Path, to: str) -> None:
    import gzip

    path = directory / "PriceFull7290103152017-001-034-20261021-110502.gz"
    xml = gzip.decompress(path.read_bytes()).replace(b"<ItemPrice>13.90</ItemPrice>", f"<ItemPrice>{to}</ItemPrice>".encode(), 1)
    path.write_bytes(gzip.compress(xml))


def test_run_publishes_triggered_alerts(client, user_headers, loaded, session, monkeypatch, tmp_path):
    import shutil

    import app.alerts.queue as queue
    from app.ingest import runner

    client.post("/api/alerts", json={"barcode": ENERGY}, headers=user_headers)
    published: list[bytes] = []
    monkeypatch.setattr(runner.settings, "RABBITMQ_URL", "amqp://test")
    monkeypatch.setattr(queue, "publish", lambda url, payloads: published.extend(payloads))
    feed = tmp_path / "osher-ad"
    shutil.copytree(FEEDS / "osher-ad", feed)
    lower_fixture_price(feed, "12.90")
    run_chain("osher-ad", feed, now=NOW + timedelta(days=1))
    assert [AlertEvent.from_json(p).price for p in published] == [12.9]


def test_broker_outage_does_not_fail_ingestion(client, user_headers, loaded, session, monkeypatch, tmp_path):
    import shutil

    import app.alerts.queue as queue
    from app.ingest import runner

    client.post("/api/alerts", json={"barcode": ENERGY}, headers=user_headers)

    def down(url, payloads):
        raise ConnectionError("broker down")

    monkeypatch.setattr(runner.settings, "RABBITMQ_URL", "amqp://test")
    monkeypatch.setattr(queue, "publish", down)
    feed = tmp_path / "osher-ad"
    shutil.copytree(FEEDS / "osher-ad", feed)
    lower_fixture_price(feed, "12.90")
    later = NOW + timedelta(days=1)
    assert run_chain("osher-ad", feed, now=later).status == "success"
    assert len(find_triggered_alerts(session, later)) == 1  # not marked as sent, so a later run can retry
