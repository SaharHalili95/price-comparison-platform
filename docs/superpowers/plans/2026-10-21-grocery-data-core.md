# Grocery Data Core (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fake electronics catalog and site scrapers with an ingestion pipeline that downloads the official supermarket price files, parses them with streaming, and stores them in PostgreSQL with change-only price history.

**Architecture:**
- **Pipeline:** per-chain *feed adapters* download files (Cerberus portal, Shufersal portal). Streaming *parsers* turn `Stores` and `PriceFull` XML into normalized records. A *loader* upserts them into PostgreSQL and writes a history row only when a price changes.
- **Entry point:** a CLI runs one chain end to end and records an ingestion run. Phase 3 wraps it in a Kubernetes CronJob.

**Tech Stack:** Python 3.12, FastAPI (kept), SQLAlchemy 2, Alembic, psycopg 3, PostgreSQL 16, lxml iterparse, httpx, respx, pytest.

**Spec:** `docs/superpowers/specs/2026-10-21-grocery-prices-design.md`

## Global Constraints

- **Feed etiquette:**
  - one download at a time per chain
  - 30s timeout
  - 3 retries with exponential backoff (2s, 4s, 8s)
  - User-Agent `SalSmart-price-ingest/1.0 (+https://github.com/SaharHalili95/price-comparison-platform)`
- **No live feeds in tests:** tests and CI never contact chain servers (CI runs outside Israel and some chains geo-block). They use the recorded samples in `backend/tests/fixtures/feeds/`.
- **Database:** PostgreSQL only, no SQLite (not even in tests). Tests run against a real Postgres: a GitHub Actions service in CI, `docker compose up -d db` locally.
- **Price history:** store a row only when `(store, item)` price differs from the latest stored price. Partition `price_history` by month (`PARTITION BY RANGE (observed_at)`).
- **Memory:** parsers stream. A 10.5 MB `PriceFull` file must parse with peak RSS growth under 50 MB.
- **Pinned versions:** exact versions, each published at least 14 days before install, and `pip-audit` clean.
- **Removed:** `app/scrapers/`, `app/data/products_database.py`, `app/services/scraper.py`, the electronics routes, `SCRAPERS_GUIDE.md`. Nothing may still import them.
- **Language:** English for code and docs, Hebrew stays in data. Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never `git add -A`.
- **README:** describes only what exists after this phase.

## Review Focus

1. **Re-running the same day's file** must add zero history rows and leave current prices unchanged.
2. **A corrupt or truncated `.gz` file** fails only that file. The run continues, and the run record lists the failure.
3. **Barcodes** are strings and keep leading zeros (`0123...`). Weighted items (`bIsWeighted=1`) keep their unit price per kg or liter.
4. **Encodings and case:** UTF-8 with a BOM, UTF-16, and the lowercase or differently-cased tags some chains use (`<Items>` vs `<items>`, `ChainID` vs `ChainId`) all parse to the same records.
5. **Stale feeds:** a chain whose newest file is older than 2 days (Keshet's latest is from 2024) is recorded as `stale`, not as a success.

---

## File Structure

```
backend/
  app/
    ingest/
      __init__.py
      records.py        StoreRecord, PriceRecord dataclasses
      parsers.py        parse_stores(), parse_prices(): streaming, tag-case-insensitive
      cities.py         city_name(code_or_name) -> str, from data/cbs_localities.csv
      feeds/
        base.py         FeedFile, FeedClient protocol, polite_get() with retry
        cerberus.py     CerberusClient (login with CSRF, list, download)
        shufersal.py    ShufersalClient (listing pages, blob download)
        chains.py       CHAINS registry: slug -> chain id, name, client factory
      loader.py         load_stores(), load_prices() -> LoadStats
      runner.py         run_chain(slug, source) -> IngestionRun
      __main__.py       CLI: python -m app.ingest <slug> [--from-dir DIR]
    models/
      grocery.py        Chain, Store, Item, CurrentPrice, IngestionRun (SQLAlchemy)
    data/cbs_localities.csv
  alembic/ + alembic.ini
  tests/
    fixtures/feeds/<chain>/Stores*.xml, PriceFull*.gz   (trimmed real samples)
    ingest/test_parsers.py test_cities.py test_feeds.py test_loader.py test_runner.py
docker-compose.yml       db service (postgres:16) used by tests and the API
```

---

### Task 1: Remove the scrapers and fake catalog, move to PostgreSQL

**Files:**
- Delete: `backend/app/scrapers/`, `backend/app/data/products_database.py`, `backend/app/services/scraper.py`, `SCRAPERS_GUIDE.md`, `frontend/src/data/mockProducts.ts` (only if unused after the API change; otherwise keep it until Phase 2 and note it)
- Modify:
  - `backend/app/api/routes.py`: keep only `GET /api/health`. The product routes return in Phase 2.
  - `backend/app/core/config.py`: `DATABASE_URL` defaults to `postgresql+psycopg://salsmart:salsmart@localhost:5432/salsmart`
  - `backend/app/core/database.py`: remove the SQLite `connect_args`
  - `backend/requirements.txt`: drop `beautifulsoup4`, `requests`, `fake-useragent`, and add `psycopg[binary]`, `alembic`
  - `docker-compose.yml`: add a `db` service `postgres:16` with a healthcheck
  - `.github/workflows/ci.yml`: Python 3.12, a postgres:16 service, `DATABASE_URL` env, plus `pip-audit`
- Test: `backend/tests/test_api.py` (trim to health and auth), `backend/tests/test_scraper.py` (delete)

**Interfaces:**
- Produces: `docker compose up -d db` gives a database reachable at the default `DATABASE_URL`. The `client` fixture in `tests/conftest.py` works against Postgres.

- [ ] **Step 1:** Write `test_health_reports_database`. `GET /api/health` returns 200 with `{"status": "ok", "database": "ok"}`, and the check runs `SELECT 1`.
- [ ] **Step 2:** Run `docker compose up -d db && cd backend && pytest tests/test_api.py -v`. Expected: FAIL (there is no database field yet, or the SQLite URL is still the default).
- [ ] **Step 3:** Delete the listed files. Rewrite `routes.py`, the config and the database setup. Update requirements and compose.
- [ ] **Step 4:** Run `grep -rn "scrapers\|products_database\|services.scraper" backend/app` (expected: nothing), then `pytest -v`. Expected: all pass.
- [ ] **Step 5: Commit** "Remove site scrapers and the hard-coded catalog" and "Move to PostgreSQL with a health check".

### Task 2: Schema and migrations

**Files:**
- Create: `backend/app/models/grocery.py`, `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/0001_grocery_schema.py`
- Modify: `backend/app/core/database.py`: `init_db()` runs `alembic upgrade head` instead of `create_all`
- Test: `backend/tests/ingest/test_schema.py`

**Interfaces:**
- **Tables:**
  - `chains(id text pk, name text, portal text)`
  - `stores(id serial pk, chain_id fk, sub_chain_id text, store_id text, name text, address text, city text, unique(chain_id, sub_chain_id, store_id))`
  - `items(barcode text pk, name text, manufacturer text, unit_of_measure text, quantity numeric, is_weighted bool)`
  - `current_prices(store_pk fk, barcode fk, price numeric(10,2), unit_price numeric(10,2) null, price_updated_at timestamptz, observed_at timestamptz, pk(store_pk, barcode))`
  - `price_history(store_pk, barcode, price, observed_at)`, `PARTITION BY RANGE (observed_at)`, with a default partition plus a function `ensure_month_partition(date)`
  - `ingestion_runs(id serial pk, chain_id, started_at, finished_at, status text check in ('running','success','partial','stale','failed'), files_ok int, files_failed int, items int, price_changes int, errors jsonb)`
- **Indexes:**
  - `items` on `name` with a `pg_trgm` GIN index (for Phase 2 search)
  - `current_prices(barcode)`
  - `stores(city)`

- [ ] **Step 1:** Write `test_migration_creates_tables`: after `alembic upgrade head`, all six tables exist and `price_history` is partitioned (`pg_partitioned_table` has a row).
- [ ] **Step 2:** Write `test_ensure_month_partition_is_idempotent`: calling it twice for `2026-10-01` creates exactly one partition named `price_history_2026_10`.
- [ ] **Step 3:** Run `pytest tests/ingest/test_schema.py -v`. Expected: FAIL.
- [ ] **Step 4:** Implement the models and the migration (the partition DDL is raw SQL in the migration).
- [ ] **Step 5:** Run the tests again. Expected: PASS. Then **commit** "Add grocery schema with partitioned price history".

### Task 3: Streaming parsers and city names

**Files:**
- Create: `backend/app/ingest/records.py`, `parsers.py`, `cities.py`, `backend/app/data/cbs_localities.csv` (CBS locality code and Hebrew name, from the government open-data CSV, committed with its source URL in a header comment line)
- Create fixtures: `backend/tests/fixtures/feeds/rami-levy/`, `osher-ad/` and `yohananof/`, each with a `Stores*.xml` and a `PriceFull*.gz` trimmed to the first 200 items, plus one store-file sample with a UTF-16 encoding and lowercase tags made from the Rami Levy sample (`stores-utf16-lowercase.xml`), plus `shufersal/` samples recorded when the portal answers (if it keeps timing out, record the ruling and add them in Task 7)
- Test: `tests/ingest/test_parsers.py`, `tests/ingest/test_cities.py`

**Interfaces:**
- **Produces:**
  - `@dataclass(frozen=True) StoreRecord(chain_id: str, sub_chain_id: str, store_id: str, name: str, address: str, city: str)`
  - `@dataclass(frozen=True) PriceRecord(chain_id: str, sub_chain_id: str, store_id: str, barcode: str, name: str, manufacturer: str, unit_of_measure: str, quantity: Decimal | None, is_weighted: bool, price: Decimal, unit_price: Decimal | None, price_updated_at: datetime)`
  - `parse_stores(source: BinaryIO) -> Iterator[StoreRecord]`
  - `parse_prices(source: BinaryIO) -> Iterator[PriceRecord]`
  - Both accept raw or gzip bytes (detect the `1f 8b` magic), detect BOM, UTF-8 or UTF-16, and match tags case-insensitively.
  - `city_name(value: str) -> str`: a numeric CBS code maps to its name, text is returned trimmed, and an unknown code is returned as-is.

- [ ] **Step 1: Write the tests**
  - `test_rami_levy_prices_parse`: 200 records. The first has barcode `'7290017023212'`, name `'רביעיית פחיות שוופס'`, price `Decimal('12.50')`, unit_price `Decimal('9.47')`, store_id `'001'`.
  - `test_barcode_keeps_leading_zeros`: a crafted item `<ItemCode>0012345</ItemCode>` gives `'0012345'`.
  - `test_weighted_item`: `bIsWeighted` 1 gives `is_weighted=True`.
  - `test_stores_parse_with_city_codes`: the Rami Levy stores file gives 99 records. Store `'001'` has name `'תלפיות'` and city `'ירושלים'`.
  - `test_utf16_and_lowercase_tags`: gives the same records as the original sample.
  - `test_streaming_memory`: parsing the full 10.5 MB sample (generated in the test by repeating fixture items) keeps the `tracemalloc` peak under 50 MB.
  - `test_unknown_city_code_kept`: `city_name('99999') == '99999'`.
- [ ] **Step 2:** Run `pytest tests/ingest/test_parsers.py tests/ingest/test_cities.py -v`. Expected: FAIL (modules missing).
- [ ] **Step 3:** Implement with `lxml.etree.iterparse` on end events, clearing each element after use. Lowercase local names before matching.
- [ ] **Step 4:** Run the tests. Expected: PASS. **Commit** "Add streaming parsers for Stores and PriceFull files" and "Map CBS locality codes to city names".

### Task 4: Feed clients

**Files:**
- Create: `backend/app/ingest/feeds/base.py`, `cerberus.py`, `shufersal.py`, `chains.py`
- Test: `tests/ingest/test_feeds.py` (respx mocks, with HTML and JSON bodies copied from real responses)

**Interfaces:**
- **Produces:**
  - `@dataclass FeedFile(name: str, kind: Literal['stores','prices'], published_at: datetime, url: str)`
  - `class FeedClient(Protocol)`:
    - `def list_files(self, kinds: set[str]) -> list[FeedFile]`
    - `def download(self, file: FeedFile) -> bytes`
  - `polite_get(client: httpx.Client, url: str, **kw) -> httpx.Response` with the retry and backoff from the Global Constraints, retrying on timeouts, 5xx and 429
  - `CerberusClient(username: str)`:
    - logs in: `GET /login`, read `csrftoken`, `POST /login/user`
    - lists files: `POST /file/json/dir` with `sSearch`
    - downloads: `GET /file/d/{name}`
  - `ShufersalClient()`:
    - lists files: `GET /FileObject/UpdateCategory?catID={2 prices|5 stores}&storeId=0&page=N` (HTML-unescape the blob URLs)
    - downloads: the blob URL
  - `CHAINS: dict[str, ChainConfig]`, where `ChainConfig(slug, chain_id, name, client: Callable[[], FeedClient])`:
    - `rami-levy` (`7290058140886`, Cerberus `RamiLevi`)
    - `osher-ad` (`7290103152017`, `osherad`)
    - `yohananof` (`7290803800003`, `yohananof`)
    - `shufersal` (`7290027600007`)
  - `published_at` is parsed from the file name (`...-YYYYMMDD-HHMMSS.gz`, or Keshet's `...-YYYYMMDDHHMM.gz`).

- [ ] **Step 1: Write the tests**
  - `test_cerberus_logs_in_with_csrf`: the POST body carries the token from the login page.
  - `test_cerberus_lists_only_requested_kinds`: `Stores` and `PriceFull` are kept, and `Price` (incremental) and `Promo` are dropped.
  - `test_retry_then_success`: two timeouts, then 200, gives 3 calls and a success.
  - `test_gives_up_after_three_retries`: raises `FeedError` after 4 attempts.
  - `test_shufersal_unescapes_blob_urls`: `&amp;` becomes `&`.
  - `test_published_at_from_names`: both name formats parse.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3:** Implement. Inject the sleep function into `polite_get` so tests don't wait.
- [ ] **Step 4:** Run. Expected: PASS. **Commit** "Add Cerberus and Shufersal feed clients with polite retries".

### Task 5: Loader with change-only history

**Files:**
- Create: `backend/app/ingest/loader.py`
- Test: `tests/ingest/test_loader.py`

**Interfaces:**
- **Consumes:** `StoreRecord`, `PriceRecord` (Task 3), and the tables (Task 2).
- **Produces:**
  - `@dataclass LoadStats(items: int, price_changes: int, unknown_stores: int)`
  - `load_stores(session, records: Iterable[StoreRecord]) -> int`: upserts and returns the count
  - `load_prices(session, records: Iterable[PriceRecord], observed_at: datetime) -> LoadStats`
  - Batches of 2,000 records.
  - Upserts `items` and `current_prices`.
  - Inserts into `price_history` only where the price is new or different, via one `INSERT ... SELECT` over a temp staging table joined to `current_prices`.
  - Calls `ensure_month_partition(observed_at)`.
  - A price for a store missing from `stores` is counted in `unknown_stores` and skipped.

- [ ] **Step 1: Write the tests**
  - `test_first_load_records_history`: 200 items give 200 history rows.
  - `test_reload_same_file_adds_nothing`: a second identical load gives `price_changes == 0`, and the history count stays the same.
  - `test_changed_price_adds_one_row`: one item at 12.50, then 11.90, gives one new row, and `current_prices` shows 11.90.
  - `test_unknown_store_is_counted_not_loaded`.
  - `test_load_of_rami_sample_under_5_seconds`: a generous bound, but it guards against row-by-row inserts.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run. Expected: PASS. **Commit** "Load prices with change-only history".

### Task 6: Runner, CLI and run records

**Files:**
- Create: `backend/app/ingest/runner.py`, `backend/app/ingest/__main__.py`, `backend/app/ingest/__init__.py`
- Test: `tests/ingest/test_runner.py`

**Interfaces:**
- **Consumes:** `CHAINS` and `FeedClient` (Task 4), the parsers (Task 3), the loader (Task 5).
- **Produces:**
  - `run_chain(slug: str, source: FeedClient | Path, now: datetime | None = None) -> IngestionRun`
  - **Steps:** create a `running` row, load the newest `Stores` file, then load each `PriceFull` (only the newest file per store). Then set the status:
    - `success`: all files ok
    - `partial`: some files failed, with errors in `errors` as `[{file, error}]`
    - `failed`: no file loaded
    - `stale`: the newest file is older than 2 days, which overrides `success`
  - `source=Path` reads files from a directory instead of the network.
  - **CLI:** `python -m app.ingest <slug> [--from-dir DIR]` prints a one-line summary. It exits 0 for `success` or `stale` and 1 for `partial` or `failed`, so the Kubernetes Job in Phase 3 shows failures.

- [ ] **Step 1: Write the tests**
  - `test_runs_fixture_directory`: status `success`, `items == 200`.
  - `test_corrupt_file_makes_partial`: add a truncated `.gz` to a temp copy of the fixtures, and expect status `partial`, `files_failed == 1`, and the other files still loaded.
  - `test_old_files_are_stale`: with `now` 5 days after the fixture dates, the status is `stale`.
  - `test_cli_exit_codes`: `success` exits 0 and `partial` exits 1 (subprocess).
  - `test_only_newest_file_per_store_is_loaded`.
- [ ] **Step 2:** Run. Expected: FAIL.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run. Expected: PASS. **Commit** "Add ingestion runner and CLI with run records".

### Task 7: Live check, docs and CI

**Files:**
- Modify: `README.md` (rewritten for what exists now), `.github/workflows/ci.yml` (from Task 1), `PROJECT_SUMMARY.md`, `QUICK_START.md` and `SETUP_GUIDE.md` (merge into the README and delete the rest)
- Create: `backend/scripts/refresh_fixtures.py`, a manual script that re-records trimmed samples from the live feeds (never run in CI)

- [ ] **Step 1:** Run, locally in Israel:

  ```bash
  python -m app.ingest rami-levy && python -m app.ingest osher-ad && python -m app.ingest yohananof && python -m app.ingest shufersal
  ```

  Record each status, item count and duration in the ledger. Shufersal may time out, and its run must then end as `failed` or `partial` without crashing.
- [ ] **Step 2:** Write the README:
  - what the data is, and the legal basis (price-transparency rules)
  - the architecture diagram of this phase
  - how to run it
  - the real numbers measured in Step 1
  - what comes next
- [ ] **Step 3:** Run `pytest -v` and `pip-audit -r backend/requirements.txt`. Expected: all pass, with no vulnerabilities.
- [ ] **Step 4: Commit** "Document the data core and remove outdated guides", then push. CI must be green.
