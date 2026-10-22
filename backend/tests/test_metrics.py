from datetime import datetime, timezone
from pathlib import Path

from app.ingest.runner import run_chain

FEEDS = Path(__file__).parent / "fixtures" / "feeds"


def test_metrics_report_each_chain(client, session):
    run_chain("osher-ad", FEEDS / "osher-ad", now=datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc))
    body = client.get("/metrics").text
    assert 'salsmart_chain_items{chain="osher-ad"} 200.0' in body
    assert 'salsmart_chain_run_status{chain="osher-ad",status="success"} 1.0' in body
    assert 'salsmart_chain_run_status{chain="osher-ad",status="failed"} 0.0' in body
    assert 'salsmart_chain_newest_file_timestamp_seconds{chain="osher-ad"}' in body
    assert "salsmart_price_alerts" in body


def test_metrics_include_http_requests(client):
    client.get("/health")
    assert 'salsmart_http_requests_total{method="GET",path="/health",status="200"}' in client.get("/metrics").text
