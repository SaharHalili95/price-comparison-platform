import gzip
import io
import subprocess
import sys
import zipfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.ingest.parsers import parse_prices, parse_stores

FEEDS = Path(__file__).parent.parent / "fixtures" / "feeds"
OSHER_PRICES = FEEDS / "osher-ad" / "PriceFull7290103152017-001-034-20261021-110502.gz"
RAMI_PRICES = FEEDS / "rami-levy" / "pricefull7290058140886-039-202610210516.gz"
YOHANANOF_PRICES = FEEDS / "yohananof" / "PriceFull7290803800003-7999-202412271528.gz"
RAMI_STORES = FEEDS / "rami-levy" / "Stores7290058140886-000-20261021-050501.xml"


def prices(path: Path):
    with path.open("rb") as source:
        return list(parse_prices(source))


def test_padded_dialect():
    records = prices(OSHER_PRICES)
    assert len(records) == 200
    first = records[0]
    assert (first.chain_id, first.sub_chain_id, first.store_id) == ("7290103152017", "1", "34")
    assert first.barcode == "7290107947473"
    assert first.name == "מאגדת אנרג'י תחתית פ"
    assert first.manufacturer == "שטראוס"
    assert first.price == Decimal("13.90")
    assert first.unit_price == Decimal("0.07")
    assert first.price_updated_at == datetime(2026, 5, 10, 11, 36, 13)


def test_unpadded_dialect_with_short_tags():
    first = prices(RAMI_PRICES)[0]
    assert (first.chain_id, first.sub_chain_id, first.store_id) == ("7290058140886", "1", "39")
    assert first.name == "פריט חדש בדיקה יוני"
    assert first.price == Decimal("30.6")
    assert first.price_updated_at == datetime(2025, 1, 19, 16, 3, 55)


def test_four_decimal_unit_price_is_kept():
    assert prices(YOHANANOF_PRICES)[0].unit_price == Decimal("0.0571")


def test_weighted_item():
    tomato = next(r for r in prices(RAMI_PRICES) if r.barcode == "100")
    assert tomato.is_weighted is True
    assert tomato.name == "עגבניה"


def test_whitespace_is_trimmed():
    tomato = next(r for r in prices(RAMI_PRICES) if r.barcode == "100")
    assert tomato.unit_of_measure == '1 ק"ג'


def test_barcode_keeps_leading_zeros():
    xml = b"<Root><ChainId>7290058140886</ChainId><SubChainId>1</SubChainId><StoreId>1</StoreId><Items><Item>" \
          b"<ItemCode>0012345</ItemCode><ItemNm>x</ItemNm><ItemPrice>1</ItemPrice></Item></Items></Root>"
    assert next(parse_prices(io.BytesIO(xml))).barcode == "0012345"


def test_zip_disguised_as_gz_is_read():
    plain = gzip.decompress(RAMI_PRICES.read_bytes())
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("pricefull.xml", plain)
    assert len(list(parse_prices(io.BytesIO(buffer.getvalue())))) == 200


def test_stores_in_utf16_with_city_names():
    with RAMI_STORES.open("rb") as source:
        stores = list(parse_stores(source))
    assert len(stores) == 99
    talpiot = stores[0]
    assert (talpiot.chain_id, talpiot.sub_chain_id, talpiot.store_id) == ("7290058140886", "1", "1")
    assert talpiot.name == "תלפיות"
    assert talpiot.city == "ירושלים"


def test_lowercase_tags_and_utf8_give_the_same_stores():
    original = RAMI_STORES.read_bytes().decode("utf-16")
    variant = original.replace("<Store>", "<store>").replace("</Store>", "</store>").replace("StoreName", "storename")
    with RAMI_STORES.open("rb") as source:
        expected = list(parse_stores(source))
    assert list(parse_stores(io.BytesIO(variant.encode("utf-8-sig")))) == expected


MEMORY_PROBE = """
import gzip, io, resource, sys
from app.ingest.parsers import parse_prices
plain = gzip.decompress(open(sys.argv[1], 'rb').read()).decode()
head, rest = plain.split('<Items>', 1)
body, tail = rest.rsplit('</Items>', 1)
big = (head + '<Items>' + body * 200 + '</Items>' + tail).encode()
before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
count = sum(1 for _ in parse_prices(io.BytesIO(big)))
after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
unit = 1 if sys.platform == 'darwin' else 1024  # ru_maxrss is bytes on macOS, KiB on Linux
print(len(big), count, (after - before) * unit)
"""


def test_large_file_streams_in_bounded_memory():
    # Measured in a fresh process: tracemalloc cannot see lxml's C allocations. Loading this 34 MB file as a whole
    # tree grows RSS by about 270 MB; streaming stays near 1 MB.
    result = subprocess.run(
        [sys.executable, "-c", MEMORY_PROBE, str(OSHER_PRICES)],
        capture_output=True, text=True, check=True, cwd=Path(__file__).parents[2],
    )
    size, count, growth = map(int, result.stdout.split())
    assert size > 30_000_000
    assert count == 200 * 200
    assert growth < 50_000_000
