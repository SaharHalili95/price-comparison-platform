"""
Re-records the trimmed sample files the tests use, from the live Cerberus portal.

Run manually from Israel (some chains block other countries); never in CI:
    cd backend && python scripts/refresh_fixtures.py
Each chain keeps its newest Stores file and one PriceFull file cut down to its first 200 items.
"""

import gzip
import io
import sys
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest.feeds.chains import CHAINS  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "feeds"
KEEP_ITEMS = 200


def unpack(raw: bytes) -> bytes:
    if raw[:2] == b"\x1f\x8b":
        return gzip.decompress(raw)
    if raw[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            return archive.read(archive.namelist()[0])
    return raw


def trim(xml: bytes) -> bytes:
    root = etree.fromstring(xml)
    items = [e for e in root.iter() if isinstance(e.tag, str) and e.tag.lower() == "item"]
    for extra in items[KEEP_ITEMS:]:
        extra.getparent().remove(extra)
    return etree.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    for slug in ("rami-levy", "osher-ad", "yohananof"):
        client = CHAINS[slug].client()
        files = client.list_files({"stores", "prices"})
        stores = max((f for f in files if f.kind == "stores"), key=lambda f: f.published_at)
        prices = max((f for f in files if f.kind == "prices"), key=lambda f: f.published_at)
        target = FIXTURES / slug
        target.mkdir(parents=True, exist_ok=True)
        (target / stores.name.removesuffix(".gz")).write_bytes(unpack(client.download(stores)))
        (target / prices.name).write_bytes(gzip.compress(trim(unpack(client.download(prices)))))
        print(f"{slug}: {stores.name}, {prices.name}")
    print("Update the expected values in tests/ingest/ to match the new samples.")


if __name__ == "__main__":
    main()
