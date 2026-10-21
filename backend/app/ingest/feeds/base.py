import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

import httpx

USER_AGENT = "SalSmart-price-ingest/1.0 (+https://github.com/SaharHalili95/price-comparison-platform)"
TIMEOUT_SECONDS = 30
BACKOFF_SECONDS = (2, 4, 8)

Kind = Literal["stores", "prices"]
Sleep = Callable[[float], None]

# PriceFull7290103152017-001-034-20261021-110502.gz, pricefull7290058140886-039-202610210516.gz
_STAMP = re.compile(r"(\d{8})-?(\d{4})(\d{2})?\.\w+$")


class FeedError(Exception):
    pass


@dataclass(frozen=True)
class FeedFile:
    name: str
    kind: Kind
    published_at: datetime
    url: str


class FeedClient(Protocol):
    def list_files(self, kinds: set[str]) -> list[FeedFile]: ...

    def download(self, file: FeedFile) -> bytes: ...


def file_kind(name: str) -> Kind | None:
    """Full price and store files only; incremental Price files and promotions are not ingested."""
    lowered = name.lower()
    if lowered.startswith("pricefull"):
        return "prices"
    if lowered.startswith("stores"):
        return "stores"
    return None


def published_at(name: str) -> datetime | None:
    match = _STAMP.search(name)
    if not match:
        return None
    day, hour_minute, seconds = match.groups()
    return datetime.strptime(day + hour_minute + (seconds or "00"), "%Y%m%d%H%M%S")


def new_client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS, follow_redirects=True)


def polite_get(client: httpx.Client, url: str, *, method: str = "GET", sleep: Sleep = time.sleep, **kwargs) -> httpx.Response:
    """One request with retries on timeouts, 5xx and 429, backing off 2, 4 then 8 seconds."""
    kwargs.setdefault("headers", {}).setdefault("User-Agent", USER_AGENT)
    last_error = ""
    for attempt, wait in enumerate((*BACKOFF_SECONDS, None)):
        try:
            response = client.request(method, url, **kwargs)
        except httpx.TransportError as error:
            last_error = f"{type(error).__name__}: {error}"
        else:
            if response.status_code < 400:
                return response
            last_error = f"HTTP {response.status_code}"
            if response.status_code != 429 and response.status_code < 500:
                raise FeedError(f"{method} {url} failed: {last_error}")
        if wait is None:
            break
        sleep(wait)
    raise FeedError(f"{method} {url} failed after {attempt + 1} attempts: {last_error}")


def to_feed_file(name: str, url: str, kinds: set[str]) -> FeedFile | None:
    kind = file_kind(name)
    when = published_at(name)
    if kind is None or kind not in kinds or when is None:
        return None
    return FeedFile(name=name, kind=kind, published_at=when, url=url)
