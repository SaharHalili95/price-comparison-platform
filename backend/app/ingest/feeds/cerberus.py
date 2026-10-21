import re
import time

import httpx

from app.ingest.feeds.base import FeedError, FeedFile, Sleep, new_client, polite_get, to_feed_file

CERBERUS_URL = "https://url.publishedprices.co.il"
_CSRF = re.compile(r'name="csrftoken"\s+content="([^"]+)"')
_SEARCH = {"stores": "Stores", "prices": "PriceFull"}


class CerberusClient:
    """The shared portal many chains publish to (Rami Levy, Osher Ad, Yohananof...). Each chain logs in with a
    public user name and an empty password; every form needs the page's CSRF token."""

    def __init__(self, username: str, sleep: Sleep = time.sleep) -> None:
        self.username = username
        self._sleep = sleep
        self._http: httpx.Client | None = None
        self._token = ""

    def _session(self) -> httpx.Client:
        if self._http is None:
            http = new_client()
            login_page = polite_get(http, f"{CERBERUS_URL}/login", sleep=self._sleep)
            form = {"username": self.username, "password": "", "csrftoken": _token(login_page.text)}
            response = polite_get(http, f"{CERBERUS_URL}/login/user", method="POST", data=form, sleep=self._sleep)
            if "/file" not in str(response.url):
                raise FeedError(f"Cerberus login failed for {self.username}")
            self._token = _token(response.text)
            self._http = http
        return self._http

    def list_files(self, kinds: set[str]) -> list[FeedFile]:
        http = self._session()
        files: list[FeedFile] = []
        for kind in sorted(kinds & _SEARCH.keys()):
            form = {"sEcho": "1", "iDisplayStart": "0", "iDisplayLength": "100000", "sSearch": _SEARCH[kind], "csrftoken": self._token}
            rows = polite_get(http, f"{CERBERUS_URL}/file/json/dir", method="POST", data=form, sleep=self._sleep).json()
            for row in rows.get("aaData", []):
                file = to_feed_file(row["fname"], f"{CERBERUS_URL}/file/d/{row['fname']}", kinds)
                if file is not None and file not in files:
                    files.append(file)
        return files

    def download(self, file: FeedFile) -> bytes:
        return polite_get(self._session(), file.url, sleep=self._sleep).content


def _token(page: str) -> str:
    match = _CSRF.search(page)
    if not match:
        raise FeedError("Cerberus page has no CSRF token")
    return match.group(1)
