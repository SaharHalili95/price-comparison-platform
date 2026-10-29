from collections.abc import Callable
from dataclasses import dataclass

from app.ingest.feeds.base import FeedClient
from app.ingest.feeds.cerberus import CerberusClient


@dataclass(frozen=True)
class ChainConfig:
    slug: str
    chain_id: str
    name: str
    portal: str
    client: Callable[[], FeedClient]


CHAINS: dict[str, ChainConfig] = {
    c.slug: c
    for c in (
        ChainConfig("rami-levy", "7290058140886", "רמי לוי", "cerberus", lambda: CerberusClient("RamiLevi")),
        ChainConfig("osher-ad", "7290103152017", "אושר עד", "cerberus", lambda: CerberusClient("osherad")),
        ChainConfig("yohananof", "7290803800003", "יוחננוף", "cerberus", lambda: CerberusClient("yohananof")),
    )
}
