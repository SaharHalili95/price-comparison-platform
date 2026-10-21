"""
Streaming parsers for the price-transparency files.

Chains publish the same data in different dialects: ChainID or ChainId, StoreID "034" or StoreId "34", ItemName or
ItemNm, ISO or space-separated dates, UTF-8 or UTF-16, and gzip, zip or plain XML (sometimes a zip named .gz). Tags
are matched case-insensitively, IDs are normalized, and elements are freed as soon as they are read, so a 10 MB file
parses in bounded memory.
"""

import gzip
import io
import zipfile
from collections.abc import Iterator
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import BinaryIO

from lxml import etree

from app.ingest.cities import city_name
from app.ingest.records import PriceRecord, StoreRecord

DATE_FORMATS = ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")


def open_xml(source: BinaryIO) -> BinaryIO:
    """Decompress by content, not by file name."""
    head = source.read(4)
    rest = source
    stream: BinaryIO = io.BufferedReader(_Prefixed(head, rest))  # type: ignore[arg-type]
    if head[:2] == b"\x1f\x8b":
        return gzip.GzipFile(fileobj=stream)  # type: ignore[return-value]
    if head[:2] == b"PK":
        archive = zipfile.ZipFile(io.BytesIO(stream.read()))
        return archive.open(archive.namelist()[0])
    return stream


class _Prefixed(io.RawIOBase):
    """Puts back the bytes read to detect the format."""

    def __init__(self, prefix: bytes, rest: BinaryIO) -> None:
        self._prefix = prefix
        self._rest = rest

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:  # type: ignore[no-untyped-def]
        if self._prefix:
            n = min(len(buffer), len(self._prefix))
            buffer[:n] = self._prefix[:n]
            self._prefix = self._prefix[n:]
            return n
        data = self._rest.read(len(buffer))
        buffer[: len(data)] = data
        return len(data)


def normalize_id(value: str) -> str:
    """'034' and '34' are the same store; some files pad IDs and some don't."""
    value = value.strip()
    return str(int(value)) if value.isdigit() else value


def _text(element: etree._Element) -> str:
    return " ".join((element.text or "").split())


def _decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value) if value else None
    except InvalidOperation:
        return None


def _datetime(value: str) -> datetime | None:
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue
    return None


def _elements(source: BinaryIO, wanted: set[str]) -> Iterator[tuple[str, etree._Element]]:
    """Yields (lowercase tag, element) for every closing tag, then frees the element and its earlier siblings."""
    for _, element in etree.iterparse(open_xml(source), events=("end",), huge_tree=True, remove_blank_text=True):
        if not isinstance(element.tag, str):
            continue
        tag = etree.QName(element).localname.lower()
        yield tag, element
        if tag in wanted:
            element.clear()
            parent = element.getparent()
            while parent is not None and element.getprevious() is not None:
                del parent[0]


def _fields(element: etree._Element) -> dict[str, str]:
    return {etree.QName(child).localname.lower(): _text(child) for child in element if isinstance(child.tag, str)}


def _first(fields: dict[str, str], *names: str) -> str:
    return next((fields[name] for name in names if fields.get(name)), "")


def parse_prices(source: BinaryIO) -> Iterator[PriceRecord]:
    header = {"chainid": "", "subchainid": "", "storeid": ""}
    for tag, element in _elements(source, {"item"}):
        if tag in header and element.getparent() is not None and element.getparent().getparent() is None:
            header[tag] = normalize_id(_text(element))
        if tag != "item":
            continue
        fields = _fields(element)
        price = _decimal(fields.get("itemprice", ""))
        barcode = fields.get("itemcode", "")
        if price is None or not barcode:
            continue
        yield PriceRecord(
            chain_id=header["chainid"],
            sub_chain_id=header["subchainid"],
            store_id=header["storeid"],
            barcode=barcode,
            name=_first(fields, "itemname", "itemnm"),
            manufacturer=_first(fields, "manufacturename", "manufacturername"),
            unit_of_measure=fields.get("unitofmeasure", ""),
            quantity=_decimal(fields.get("quantity", "")),
            is_weighted=fields.get("bisweighted") == "1",
            price=price,
            unit_price=_decimal(fields.get("unitofmeasureprice", "")),
            price_updated_at=_datetime(_first(fields, "priceupdatetime", "priceupdatedate")),
        )


def parse_stores(source: BinaryIO) -> Iterator[StoreRecord]:
    chain_id = sub_chain_id = ""
    for tag, element in _elements(source, {"store"}):
        if tag == "chainid":
            chain_id = normalize_id(_text(element))
        elif tag == "subchainid" and element.getparent() is not None and element.getparent().tag.lower() != "store":
            sub_chain_id = normalize_id(_text(element))
        elif tag == "store":
            fields = _fields(element)
            yield StoreRecord(
                chain_id=chain_id,
                sub_chain_id=normalize_id(fields.get("subchainid", sub_chain_id)),
                store_id=normalize_id(fields.get("storeid", "")),
                name=fields.get("storename", ""),
                address=fields.get("address", ""),
                city=city_name(fields.get("city", "")),
            )
