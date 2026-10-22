"""Runs one chain end to end: newest store list, then the newest full price file of every store."""

import io
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.alerts.events import find_triggered_alerts, mark_notified
from app.core.config import settings
from app.core.database import SessionLocal
from app.ingest.feeds.base import FeedClient, FeedFile, to_feed_file
from app.ingest.feeds.chains import CHAINS
from app.ingest.loader import ensure_chain, load_prices, load_stores
from app.ingest.parsers import normalize_id, parse_prices, parse_stores
from app.models.grocery import IngestionRun

logger = logging.getLogger(__name__)

STALE_AFTER = timedelta(days=2)
# A store's file this much older than the chain's newest file is a leftover from a closed store.
LEFTOVER_AFTER = timedelta(days=30)
ISRAEL = ZoneInfo("Asia/Jerusalem")
# PriceFull<chain>-<sub>-<store>-<date>... or pricefull<chain>-<store>-<date>...: the store is the part before the date.
_STORE_IN_NAME = re.compile(r"-(\d+)-\d{8}(?:-?\d{4,6})?\.\w+$")


class DirectorySource:
    """Reads files saved on disk instead of the network: tests, and re-running a saved day."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def list_files(self, kinds: set[str]) -> list[FeedFile]:
        files = (to_feed_file(p.name, str(p), kinds) for p in sorted(self.directory.iterdir()) if p.is_file())
        return [f for f in files if f is not None]

    def download(self, file: FeedFile) -> bytes:
        return Path(file.url).read_bytes()


def _store_of(file: FeedFile) -> str:
    match = _STORE_IN_NAME.search(file.name)
    return normalize_id(match.group(1)) if match else file.name


def _newest_per_store(files: list[FeedFile]) -> list[FeedFile]:
    newest: dict[str, FeedFile] = {}
    for file in files:
        current = newest.get(_store_of(file))
        if current is None or file.published_at > current.published_at:
            newest[_store_of(file)] = file
    if not newest:
        return []
    cutoff = max(f.published_at for f in newest.values()) - LEFTOVER_AFTER
    return sorted((f for f in newest.values() if f.published_at >= cutoff), key=lambda f: f.name)


def run_chain(slug: str, source: FeedClient | Path, now: datetime | None = None, max_stores: int | None = None) -> IngestionRun:
    config = CHAINS[slug]
    client = DirectorySource(source) if isinstance(source, Path) else source
    now = now or datetime.now(timezone.utc)
    session: Session = SessionLocal()
    try:
        ensure_chain(session, chain_id=config.chain_id, slug=config.slug, name=config.name, portal=config.portal)
        run = IngestionRun(chain_id=config.chain_id, started_at=now, status="running", errors=[])
        session.add(run)
        session.commit()

        # Counted locally: a rollback after a bad file would otherwise reset counters held on the ORM object.
        errors: list[dict[str, str]] = []
        files_ok = files_failed = items = price_changes = 0
        try:
            files = client.list_files({"stores", "prices"})
        except Exception as error:  # an unreachable portal is a failed run, not a crash that leaves it "running"
            logger.warning("Could not list files for %s: %s", slug, error)
            errors.append({"file": "(listing)", "error": f"{type(error).__name__}: {error}"})
            files = []
        store_files = sorted((f for f in files if f.kind == "stores"), key=lambda f: f.published_at)
        price_files = _newest_per_store([f for f in files if f.kind == "prices"])[:max_stores]

        for file in store_files[-1:] + price_files:
            try:
                data = io.BytesIO(client.download(file))
                if file.kind == "stores":
                    load_stores(session, parse_stores(data))
                else:
                    stats = load_prices(session, parse_prices(data), now)
                    if stats.items == 0 and stats.unknown_stores:
                        raise ValueError(f"{stats.unknown_stores} prices for a store not in the store list")
                    items += stats.items
                    price_changes += stats.price_changes
                files_ok += 1
            except Exception as error:  # one bad file must not stop the rest of the chain
                session.rollback()
                logger.warning("Failed to ingest %s: %s", file.name, error)
                errors.append({"file": file.name, "error": f"{type(error).__name__}: {error}"})
                files_failed += 1

        run.files_ok, run.files_failed, run.items, run.price_changes = files_ok, files_failed, items, price_changes
        newest = max((f.published_at for f in price_files), default=None)
        run.newest_file_at = newest.replace(tzinfo=ISRAEL) if newest else None
        run.errors = errors
        run.finished_at = datetime.now(timezone.utc)
        if run.files_ok == 0:
            run.status = "failed"
        elif run.files_failed:
            run.status = "partial"
        elif run.newest_file_at is None or now - run.newest_file_at > STALE_AFTER:
            run.status = "stale"
        else:
            run.status = "success"
        session.commit()
        _publish_alerts(session, now)
        session.refresh(run)
        session.expunge(run)
        return run
    finally:
        session.close()


def _publish_alerts(session: Session, observed_at: datetime) -> None:
    """Hands triggered alerts to RabbitMQ. A broker outage is logged and never fails the ingestion."""
    if not settings.RABBITMQ_URL:
        return
    from app.alerts.queue import publish

    events = find_triggered_alerts(session, observed_at)
    if not events:
        return
    try:
        publish(settings.RABBITMQ_URL, [e.to_json() for e in events])
    except Exception:
        logger.exception("Could not publish %d price alerts", len(events))
        return
    mark_notified(session, [e.alert_id for e in events], observed_at)
    logger.info("Published %d price alerts", len(events))
