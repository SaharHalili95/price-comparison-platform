"""python -m app.ingest <chain> [--from-dir DIR]: exits 1 when files failed, so a Kubernetes Job shows it."""

import argparse
import logging
import sys
from pathlib import Path

from app.ingest.feeds.chains import CHAINS
from app.ingest.runner import run_chain


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m app.ingest", description="Ingest one chain's price files.")
    parser.add_argument("chain", choices=sorted(CHAINS))
    parser.add_argument("--max-stores", type=int, default=5, help="stores per chain (prototype default 5; 0 for all)")
    parser.add_argument("--from-dir", type=Path, help="read saved files from this directory instead of the portal")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    run = run_chain(args.chain, args.from_dir or CHAINS[args.chain].client(), max_stores=args.max_stores or None)
    duration = (run.finished_at - run.started_at).total_seconds() if run.finished_at else 0
    print(
        f"{args.chain}: {run.status} | files ok {run.files_ok}, failed {run.files_failed} | "
        f"items {run.items}, price changes {run.price_changes} | newest file {run.newest_file_at} | {duration:.1f}s"
    )
    return 1 if run.status in ("partial", "failed") else 0


if __name__ == "__main__":
    sys.exit(main())
