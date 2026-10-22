"""
Prometheus metrics at /metrics.

Ingestion runs as short-lived Jobs, so instead of each Job pushing metrics, the API reports the latest run per
chain from the database on every scrape. Grafana alerts when a chain's newest file gets old or its run fails.
"""

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, generate_latest
from prometheus_client.core import GaugeMetricFamily
from sqlalchemy import text

from app.core.database import SessionLocal

STATUSES = ("success", "partial", "stale", "failed", "running")
registry = CollectorRegistry()
http_requests = Counter("salsmart_http_requests", "HTTP requests", ["method", "path", "status"], registry=registry)


class IngestionCollector:
    def collect(self):  # type: ignore[no-untyped-def]
        items = GaugeMetricFamily("salsmart_chain_items", "Prices loaded by the latest run", labels=["chain"])
        changes = GaugeMetricFamily("salsmart_chain_price_changes", "Price changes in the latest run", labels=["chain"])
        failed = GaugeMetricFamily("salsmart_chain_files_failed", "Files that failed in the latest run", labels=["chain"])
        newest = GaugeMetricFamily("salsmart_chain_newest_file_timestamp_seconds", "Publish time of the newest file", labels=["chain"])
        status = GaugeMetricFamily("salsmart_chain_run_status", "1 for the status of the latest run", labels=["chain", "status"])
        alerts = GaugeMetricFamily("salsmart_price_alerts", "Price alerts users have set")
        with SessionLocal() as db:
            rows = db.execute(
                text(
                    "SELECT DISTINCT ON (r.chain_id) ch.slug, r.status, r.items, r.price_changes, r.files_failed, r.newest_file_at "
                    "FROM ingestion_runs r JOIN chains ch ON ch.id = r.chain_id ORDER BY r.chain_id, r.started_at DESC"
                )
            ).mappings()
            for r in rows:
                items.add_metric([r["slug"]], r["items"])
                changes.add_metric([r["slug"]], r["price_changes"])
                failed.add_metric([r["slug"]], r["files_failed"])
                if r["newest_file_at"]:
                    newest.add_metric([r["slug"]], r["newest_file_at"].timestamp())
                for s in STATUSES:
                    status.add_metric([r["slug"], s], 1 if r["status"] == s else 0)
            alerts.add_metric([], db.execute(text("SELECT count(*) FROM price_alerts")).scalar_one())
        yield from (items, changes, failed, newest, status, alerts)


registry.register(IngestionCollector())


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def count_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        # The route template, not the raw URL, so /api/items/123 and /api/items/456 share one series.
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")
        http_requests.labels(request.method, path, str(response.status_code)).inc()
        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
