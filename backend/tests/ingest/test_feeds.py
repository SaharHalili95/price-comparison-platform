from datetime import datetime
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from app.ingest.feeds.base import USER_AGENT, FeedError, FeedFile, file_kind, polite_get, published_at
from app.ingest.feeds.cerberus import CERBERUS_URL, CerberusClient
from app.ingest.feeds.chains import CHAINS
from app.ingest.feeds.shufersal import SHUFERSAL_URL, ShufersalClient

LOGIN_PAGE = '<html><head><meta name="csrftoken" content="login-token"></head></html>'
FILES_PAGE = '<html><head><meta name="csrftoken" content="files-token"></head></html>'


def no_sleep(_seconds: float) -> None:
    pass


@pytest.mark.parametrize(
    ("name", "kind", "when"),
    [
        ("PriceFull7290103152017-001-034-20261021-110502.gz", "prices", datetime(2026, 10, 21, 11, 5, 2)),
        ("pricefull7290058140886-039-202610210516.gz", "prices", datetime(2026, 10, 21, 5, 16)),
        ("Stores7290058140886-000-20261021-050501.xml", "stores", datetime(2026, 10, 21, 5, 5, 1)),
        ("Price7290058140886-001-001-20261021-121500.gz", None, datetime(2026, 10, 21, 12, 15)),
        ("PromoFull7290058140886-001-001-20261021-001002.gz", None, datetime(2026, 10, 21, 0, 10, 2)),
    ],
)
def test_names_give_kind_and_time(name, kind, when):
    assert file_kind(name) == kind
    assert published_at(name) == when


@respx.mock
def test_retry_then_success():
    route = respx.get("https://feed.test/file").mock(
        side_effect=[httpx.ConnectTimeout("slow"), httpx.Response(503), httpx.Response(200, text="ok")]
    )
    with httpx.Client() as client:
        assert polite_get(client, "https://feed.test/file", sleep=no_sleep).text == "ok"
    assert route.call_count == 3
    assert route.calls[0].request.headers["User-Agent"] == USER_AGENT


@respx.mock
def test_gives_up_after_three_retries():
    route = respx.get("https://feed.test/file").mock(side_effect=httpx.ReadTimeout("slow"))
    waits: list[float] = []
    with httpx.Client() as client, pytest.raises(FeedError):
        polite_get(client, "https://feed.test/file", sleep=waits.append)
    assert route.call_count == 4
    assert waits == [2, 4, 8]


@respx.mock
def test_client_errors_are_not_retried():
    route = respx.get("https://feed.test/file").mock(return_value=httpx.Response(404))
    with httpx.Client() as client, pytest.raises(FeedError):
        polite_get(client, "https://feed.test/file", sleep=no_sleep)
    assert route.call_count == 1


def mock_cerberus(names: list[str]):
    respx.get(f"{CERBERUS_URL}/login").mock(return_value=httpx.Response(200, text=LOGIN_PAGE))
    login = respx.post(f"{CERBERUS_URL}/login/user").mock(
        return_value=httpx.Response(302, headers={"Location": f"{CERBERUS_URL}/file"})
    )
    respx.get(f"{CERBERUS_URL}/file").mock(return_value=httpx.Response(200, text=FILES_PAGE))

    def listing(request: httpx.Request) -> httpx.Response:
        search = parse_qs(request.content.decode())["sSearch"][0]
        return httpx.Response(200, json={"aaData": [{"fname": n} for n in names if search.lower() in n.lower()]})

    directory = respx.post(f"{CERBERUS_URL}/file/json/dir").mock(side_effect=listing)
    return login, directory


@respx.mock
def test_cerberus_logs_in_with_the_page_token():
    login, directory = mock_cerberus(["Stores7290058140886-000-20261021-050501.xml"])
    CerberusClient("RamiLevi", sleep=no_sleep).list_files({"stores"})
    form = parse_qs(login.calls[0].request.content.decode(), keep_blank_values=True)
    assert form == {"username": ["RamiLevi"], "password": [""], "csrftoken": ["login-token"]}
    assert parse_qs(directory.calls[0].request.content.decode())["csrftoken"] == ["files-token"]


@respx.mock
def test_cerberus_lists_only_full_price_and_store_files():
    mock_cerberus([
        "Stores7290058140886-000-20261021-050501.xml",
        "PriceFull7290058140886-001-001-20261021-001002.gz",
        "Price7290058140886-001-001-20261021-121500.gz",
        "PromoFull7290058140886-001-001-20261021-001002.gz",
    ])
    files = CerberusClient("RamiLevi", sleep=no_sleep).list_files({"stores", "prices"})
    assert sorted((f.kind, f.name) for f in files) == [
        ("prices", "PriceFull7290058140886-001-001-20261021-001002.gz"),
        ("stores", "Stores7290058140886-000-20261021-050501.xml"),
    ]
    assert all(f.url.startswith(f"{CERBERUS_URL}/file/d/") for f in files)


@respx.mock
def test_cerberus_rejected_login_raises():
    respx.get(f"{CERBERUS_URL}/login").mock(return_value=httpx.Response(200, text=LOGIN_PAGE))
    respx.post(f"{CERBERUS_URL}/login/user").mock(return_value=httpx.Response(200, text=LOGIN_PAGE))
    with pytest.raises(FeedError, match="login"):
        CerberusClient("NoSuchChain", sleep=no_sleep).list_files({"prices"})


@respx.mock
def test_shufersal_unescapes_blob_urls_and_pages():
    blob = "https://pricesprodpublic.blob.core.windows.net/pricefull/PriceFull7290027600007-001-001-20261021-043100.gz"
    page_one = f'<a href="{blob}?sv=2014-02-14&amp;sr=b&amp;sig=abc">x</a>'
    respx.get(f"{SHUFERSAL_URL}/FileObject/UpdateCategory", params={"catID": "2", "page": "1"}).mock(
        return_value=httpx.Response(200, text=page_one)
    )
    respx.get(f"{SHUFERSAL_URL}/FileObject/UpdateCategory", params={"catID": "2", "page": "2"}).mock(
        return_value=httpx.Response(200, text="<html></html>")
    )
    files = ShufersalClient(sleep=no_sleep).list_files({"prices"})
    assert [f.name for f in files] == ["PriceFull7290027600007-001-001-20261021-043100.gz"]
    assert files[0].url == f"{blob}?sv=2014-02-14&sr=b&sig=abc"
    assert files[0].kind == "prices"


@respx.mock
def test_download_returns_bytes():
    respx.get("https://feed.test/a.gz").mock(return_value=httpx.Response(200, content=b"\x1f\x8bdata"))
    file = FeedFile(name="a.gz", kind="prices", published_at=datetime(2026, 10, 21), url="https://feed.test/a.gz")
    assert ShufersalClient(sleep=no_sleep).download(file) == b"\x1f\x8bdata"


def test_registry_has_the_four_chains():
    assert {slug: c.chain_id for slug, c in CHAINS.items()} == {
        "rami-levy": "7290058140886",
        "osher-ad": "7290103152017",
        "yohananof": "7290803800003",
        "shufersal": "7290027600007",
    }
