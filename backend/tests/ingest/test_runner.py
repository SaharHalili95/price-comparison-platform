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
