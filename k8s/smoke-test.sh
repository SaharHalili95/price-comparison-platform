#!/usr/bin/env bash
# Builds both images, deploys the local overlay to a kind cluster, ingests the recorded samples and queries the API.
# Used by CI and runnable locally: k8s/smoke-test.sh
set -euo pipefail
CLUSTER=${CLUSTER:-salsmart}
cd "$(dirname "$0")/.."

kind get clusters | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER" --wait 120s
docker build -q -t salsmart-api:local . >/dev/null
docker build -q -t salsmart-web:local frontend >/dev/null
kind load docker-image --name "$CLUSTER" salsmart-api:local salsmart-web:local

kubectl apply -k k8s/overlays/local
kubectl -n salsmart rollout status statefulset/db --timeout=180s
kubectl -n salsmart rollout status deployment/api --timeout=180s
kubectl -n salsmart rollout status deployment/web --timeout=120s
kubectl -n salsmart wait --for=condition=complete job/smoke-ingest --timeout=300s
kubectl -n salsmart rollout status statefulset/rabbitmq --timeout=240s
kubectl -n salsmart rollout status deployment/notifier --timeout=240s

kubectl -n salsmart port-forward service/web 8088:80 >/dev/null 2>&1 &
trap 'kill $(jobs -p) 2>/dev/null' EXIT
for _ in $(seq 30); do curl -sf localhost:8088/api/status >/dev/null && break; sleep 1; done
status=$(curl -sf localhost:8088/api/status)
echo "status: $status"
echo "$status" | grep -Eq '"status":"(success|stale)"'  # the recorded samples age into stale
curl -sf "localhost:8088/api/items/7290107947473" | grep -q '"price":13.9'
curl -sf localhost:8088/ | grep -q SalSmart
for _ in $(seq 30); do kubectl -n salsmart logs deployment/notifier 2>/dev/null | grep -q "Waiting for price alerts" && break; sleep 2; done
kubectl -n salsmart logs deployment/notifier | grep -q "Waiting for price alerts"
# End to end: a published alert must come out of the notifier as an email in Mailpit.
kubectl -n salsmart exec deployment/notifier -- python -c "
from app.alerts.events import AlertEvent
from app.alerts.queue import publish
from app.core.config import settings
publish(settings.RABBITMQ_URL, [AlertEvent(0, 'smoke@example.com', '1', 'smoke-item', 1.0, 2.0, 'chain', 'store').to_json()])"
kubectl -n salsmart port-forward service/mailpit 8025:8025 >/dev/null 2>&1 &
for _ in $(seq 30); do curl -sf localhost:8025/api/v1/messages | grep -q smoke-item && break; sleep 1; done
curl -sf localhost:8025/api/v1/messages | grep -q smoke-item
echo "alert email delivered"

kubectl -n salsmart rollout status deployment/prometheus --timeout=180s
kubectl -n salsmart rollout status deployment/grafana --timeout=180s
kubectl -n salsmart port-forward service/prometheus 9090:9090 >/dev/null 2>&1 &
for _ in $(seq 90); do curl -sf "localhost:9090/api/v1/query?query=salsmart_chain_items" | grep -q osher-ad && break; sleep 2; done
curl -sf "localhost:9090/api/v1/query?query=salsmart_chain_items" | grep -q osher-ad
curl -sf "localhost:9090/api/v1/rules" | grep -q ChainDataStale
echo "prometheus scrapes the API and has the alert rules"
kubectl -n salsmart get cronjobs
echo "kind smoke test passed"
