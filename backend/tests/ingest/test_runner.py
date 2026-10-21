import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from app.ingest.runner import run_chain

FIXTURE = Path(__file__).parent.parent / "fixtures" / "feeds" / "osher-ad"
PRICES = "PriceFull7290103152017-001-034-20261021-110502.gz"
SAME_DAY = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
BACKEND = Path(__file__).parents[2]


@pytest.fixture
def feed_dir(tmp_path: Path) -> Path:
    target = tmp_path / "osher-ad"
    shutil.copytree(FIXTURE, target)
    return target


def test_runs_a_fixture_directory(session, feed_dir):
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY)
    assert run.status == "success"
    assert (run.files_ok, run.files_failed, run.items, run.price_changes) == (2, 0, 200, 200)
    assert run.newest_file_at is not None
    assert session.execute(text("SELECT count(*) FROM stores")).scalar_one() == 24


def test_corrupt_file_makes_the_run_partial(session, feed_dir):
    good = (feed_dir / PRICES).read_bytes()
    (feed_dir / "PriceFull7290103152017-001-035-20261021-110502.gz").write_bytes(good[: len(good) // 2])
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY)
    assert run.status == "partial"
    assert run.files_failed == 1
    assert run.items == 200
    assert run.errors[0]["file"] == "PriceFull7290103152017-001-035-20261021-110502.gz"


def test_nothing_loaded_is_a_failure(session, tmp_path):
    empty = tmp_path / "osher-ad"
    empty.mkdir()
    assert run_chain("osher-ad", empty, now=SAME_DAY).status == "failed"


def test_old_files_are_stale(session, feed_dir):
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY + timedelta(days=5))
    assert run.status == "stale"


def test_only_the_newest_file_per_store_is_loaded(session, feed_dir):
    shutil.copy(feed_dir / PRICES, feed_dir / "PriceFull7290103152017-001-034-20261019-110502.gz")
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY)
    assert run.files_ok == 2
    assert run.items == 200


def test_run_is_recorded(session, feed_dir):
    run_chain("osher-ad", feed_dir, now=SAME_DAY)
    row = session.execute(text("SELECT status, items FROM ingestion_runs")).one()
    assert tuple(row) == ("success", 200)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.ingest", *args], cwd=BACKEND, env=os.environ.copy(), capture_output=True, text=True
    )


def test_cli_exit_codes(session, feed_dir):
    ok = run_cli("osher-ad", "--from-dir", str(feed_dir))
    assert ok.returncode == 0, ok.stderr
    assert "osher-ad" in ok.stdout
    good = (feed_dir / PRICES).read_bytes()
    (feed_dir / "PriceFull7290103152017-001-035-20261021-110502.gz").write_bytes(good[:100])
    assert run_cli("osher-ad", "--from-dir", str(feed_dir)).returncode == 1


def test_cli_rejects_unknown_chain():
    result = run_cli("no-such-chain")
    assert result.returncode == 2


def test_file_matching_no_store_is_a_failure(session, feed_dir):
    (feed_dir / PRICES).rename(feed_dir / "PriceFull7290103152017-001-034-20261021-110502.gz")
    for store_file in feed_dir.glob("Stores*.xml"):
        text_ = store_file.read_bytes().decode("utf-16").replace("<StoreID>034</StoreID>", "<StoreID>934</StoreID>")
        store_file.write_bytes(text_.encode("utf-16"))
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY)
    assert run.status == "partial"
    assert run.items == 0
    assert "not in the store list" in run.errors[0]["error"]


def test_files_long_older_than_the_chain_are_ignored(session, feed_dir):
    # Yohananof still lists a December 2024 file for a store that has since closed.
    shutil.copy(feed_dir / PRICES, feed_dir / "PriceFull7290103152017-001-799-20241227-152800.gz")
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY)
    assert run.status == "success"
    assert run.files_ok == 2


class UnreachablePortal:
    def list_files(self, kinds):
        from app.ingest.feeds.base import FeedError

        raise FeedError("GET https://prices.shufersal.co.il failed after 4 attempts: ReadTimeout")

    def download(self, file):
        raise AssertionError("nothing to download")


def test_unreachable_portal_is_recorded_as_failed(session):
    run = run_chain("shufersal", UnreachablePortal(), now=SAME_DAY)
    assert run.status == "failed"
    assert run.finished_at is not None
    assert "ReadTimeout" in run.errors[0]["error"]
    stored = session.execute(text("SELECT status FROM ingestion_runs")).scalar_one()
    assert stored == "failed"


def test_max_stores_limits_the_price_files(session, feed_dir):
    shutil.copy(feed_dir / PRICES, feed_dir / "PriceFull7290103152017-001-035-20261021-110502.gz")
    run = run_chain("osher-ad", feed_dir, now=SAME_DAY, max_stores=1)
    assert run.files_ok == 2  # the store list plus one price file
