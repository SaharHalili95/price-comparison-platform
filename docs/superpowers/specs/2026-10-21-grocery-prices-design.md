# Grocery price comparison on official price-transparency data

## Intent

`price-comparison-platform` is one of Sahar's portfolio projects. Today it compares electronics using a hand-written catalog of fixed prices, plus scrapers for Zap, KSP and Bug that are fragile and against those sites' terms. The live demo runs on mock data.

We are rebuilding its core around **real, legal, public data**: under Israel's price-transparency rules, supermarket chains publish full daily price files for every store. The product becomes a grocery price comparison for Israeli shoppers: find a product, see what it costs in each chain and store, and compare a whole basket.

The project has a second job in the portfolio. **SalaryNet** proves C# / .NET. **This project proves a Python data platform**: ingestion of large files in parallel, a real database at scale, a message queue, Kubernetes, and monitoring. Each technology must solve a problem the system actually has, so Sahar can explain it in one sentence in an interview.

## The problem the data creates (and why each technology is here)

Verified on 2026-10-21:
- **Rami Levy (Cerberus portal):** one store's `PriceFull` file is about 1 MB gzipped, 10.5 MB of XML, and about 13,000 items. Rami Levy alone has dozens of stores.
- **Shufersal (its own portal):** listing and file URLs work, but the server answered once and then timed out on every retry.

| Need | Technology | How a visitor sees the benefit |
| --- | --- | --- |
| Download and parse hundreds of MB of XML per day from many chains, in parallel, and one failing chain must not stop the others | **Kubernetes CronJobs** (one per chain) with retries and resource limits | An "Ingestion status" page: per-chain last success, duration, item count |
| Feeds are slow and unreliable (Shufersal timed out) | Kubernetes `backoffLimit` and restarts, plus retry with backoff in the downloader | A failed chain shows as late on the status page, then recovers by itself |
| Millions of price rows, queries like "cheapest basket near me" | **PostgreSQL**: price history stored only when a price changes, indexes, and partitioning by month | README shows a query plan before and after an index, with timings |
| "Tell me when this product gets cheaper" | **RabbitMQ**: the ingestion publishes price changes, and a notifier worker sends the email | Stop the notifier: ingestion keeps running, and emails go out when it comes back |
| Save baskets and alerts per person | **OAuth 2.0 / OpenID Connect** sign-in with Google | No passwords to store |
| Know when a chain stopped publishing or parsing broke | **Prometheus metrics and Grafana** dashboards and alerts | Dashboard: files and items per chain per day, failures, queue depth |

## Goals

- Ingest `Stores` and `PriceFull` files from at least 4 chains:
  - 3 on the shared Cerberus portal (Rami Levy plus two others, chosen when they are verified to work)
  - Shufersal on its own portal
- Normalize every chain's data into one schema: chain, store (with city), item (barcode, name, manufacturer, unit), and price.
- **Search:** find products by name or barcode and see the price in each chain and store, with the date the price was last updated.
- **Basket:** pick products, choose a city, and see the total per store, cheapest first. Missing items are shown as missing, not ignored.
- **Price alerts** by email through the queue.
- Everything runs on a Kubernetes cluster with free hosting, plus a public read-only demo.
- Tests and CI at the same standard as SalaryNet, with honest README numbers.

## Non-goals

- Promotions files (`PromoFull`) in the first release. Store the files, but don't parse promotions yet. They are complex and come next.
- Mobile apps, payments, user-generated content.
- Rewriting the backend in .NET (decided with Sahar: Python, because SalaryNet already covers .NET).
- Real-time intraday prices. One full ingestion per day is enough.

## Anti-goals

- Scraping sites that do not publish data for this purpose. The old Zap, KSP and Bug scrapers and the hard-coded electronics catalog are removed.
- Technologies with no job in the system (no Kafka next to RabbitMQ, no service mesh, no microservice per table).
- Claiming numbers the system does not produce, such as product counts or chain counts.
- A dead live demo. If a chain stops publishing, the site says so with its last good date. It never shows silently stale data.

## Constraints

- **Geo-blocking:** some chains block downloads from outside Israel.
  - The production ingestion must run from an Israeli region. Oracle Cloud **Jerusalem** is the first candidate for an Always Free VM running **k3s**. Azure **Israel Central** is the fallback if Jerusalem has no Always Free capacity.
  - CI runners are in the US, so tests use **recorded sample files** committed to the repo (trimmed to a few hundred items) and never download from chains.
- **Free:** every hosted piece must be on a free tier:
  - Oracle Always Free (or a credit-funded Azure alternative only if Sahar agrees)
  - Grafana Cloud free
  - CloudAMQP free or RabbitMQ in-cluster
  - Brevo or Resend free email
  - Google OAuth
  The cloud account sign-up is done by Sahar (it needs a credit card for verification), and a budget alert is set on day one.
- **Disk and database:** the database must fit the free VM. Store a price row only when the price changes (change data capture by comparison), keep raw files 7 days, and partition history by month.
- **Pinned versions:** exact dependency versions, each published at least two weeks before it is installed, `npm audit` / `pip-audit` clean.
- **Code style:** English for code and docs, Hebrew in the UI, commit style as in Sahar's other repos (no em dashes, many small commits).
- **Feed handling:** be polite to the chains. One download at a time per chain, a timeout, retry with backoff, and an identifying User-Agent.

## Decisions

### Decided with Sahar
- Improve the existing `price-comparison-platform` rather than start a new repo.
- Pivot from electronics to supermarkets using the official price files.
- Keep Python (FastAPI) for the backend. Keep React + TypeScript for the front end.
- Kubernetes is in because the ingestion genuinely needs parallel, isolated, retried jobs.

### My calls (Sahar can override)
- **Database: PostgreSQL** instead of SQLite.
- **Queue: RabbitMQ in-cluster.** It is simpler to show and costs nothing on the VM, with CloudAMQP free as the fallback.
- **Local and CI cluster: kind**, plus Kubernetes manifests with Kustomize (base plus overlays for local and production). No Helm charts of our own.
- **The existing auth, rate limiting and audit log** in the backend stay and are extended with Google sign-in. Email and password sign-in can stay for the demo account.
- **Repository visibility:** it is private today. It goes public when the first release is live, and Sahar confirms that step.

## Phases

1. **Data core.**
   - Chain adapters (Cerberus, Shufersal), a normalizer, the PostgreSQL schema with change-only history, and an ingestion CLI tested on recorded files.
   - Remove the scrapers and the fake catalog.
2. **API and UI.** Search, product page across chains, basket per city, and the ingestion status page. Update the React UI.
3. **Kubernetes.** Container images, Kustomize manifests (CronJob per chain, API, worker, Postgres, RabbitMQ), kind in CI with a smoke test.
4. **Queue and alerts.** Price-change events, notifier worker, email, Google sign-in, saved baskets and alerts.
5. **Monitoring and hosting.**
   - Prometheus metrics, Grafana dashboards.
   - Deploy to the free Israeli VM on k3s, with the public demo.
   - README, CV and portfolio update.

Each phase ends with CI green and a README that describes only what exists.

## Left to the builder
- Exact libraries (for example `lxml` iterparse vs `xml.etree`, SQLAlchemy vs raw SQL for bulk upserts), as long as a 10 MB file parses with streaming and bounded memory.
- Which two other Cerberus chains, after checking they publish today.
- UI layout details.
- The specific partitioning and index choices, as long as the README documents one measured before/after improvement.
