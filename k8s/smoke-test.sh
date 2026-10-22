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

kubectl -n salsmart port-forward service/web 8088:80 >/dev/null 2>&1 &
trap 'kill %1' EXIT
for _ in $(seq 30); do curl -sf localhost:8088/api/status >/dev/null && break; sleep 1; done
status=$(curl -sf localhost:8088/api/status)
echo "status: $status"
echo "$status" | grep -Eq '"status":"(success|stale)"'  # the recorded samples age into stale
curl -sf "localhost:8088/api/items/7290107947473" | grep -q '"price":13.9'
curl -sf localhost:8088/ | grep -q SalSmart
kubectl -n salsmart get cronjobs
echo "kind smoke test passed"
