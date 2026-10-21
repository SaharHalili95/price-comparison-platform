import html
import re
import time
from urllib.parse import unquote, urlparse

import httpx

from app.ingest.feeds.base import FeedFile, Sleep, new_client, polite_get, to_feed_file

SHUFERSAL_URL = "https://prices.shufersal.co.il"
_CATEGORIES = {"prices": 2, "stores": 5}
_LINK = re.compile(r'href="(https://pricesprodpublic\.blob\.core\.windows\.net/[^"]+)"')
MAX_PAGES = 200


class ShufersalClient:
    """Shufersal's own portal: paged HTML listings that link to time-limited Azure blob URLs."""

    def __init__(self, sleep: Sleep = time.sleep) -> None:
        self._sleep = sleep
        self._http: httpx.Client | None = None

    def _session(self) -> httpx.Client:
        if self._http is None:
            self._http = new_client()
        return self._http

    def list_files(self, kinds: set[str]) -> list[FeedFile]:
        files: list[FeedFile] = []
        for kind in sorted(kinds & _CATEGORIES.keys()):
            for page in range(1, MAX_PAGES + 1):
                listing = polite_get(
                    self._session(), f"{SHUFERSAL_URL}/FileObject/UpdateCategory",
                    params={"catID": _CATEGORIES[kind], "storeId": 0, "page": page}, sleep=self._sleep,
                )
                links = [html.unescape(link) for link in _LINK.findall(listing.text)]
                if not links:
                    break
                for url in links:
                    file = to_feed_file(unquote(urlparse(url).path.rsplit("/", 1)[-1]), url, kinds)
                    if file is not None:
                        files.append(file)
        return files

    def download(self, file: FeedFile) -> bytes:
        return polite_get(self._session(), file.url, sleep=self._sleep).content
