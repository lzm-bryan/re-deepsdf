#!/usr/bin/env bash
set -euo pipefail

BASELINE_ROOT="${BASELINE_ROOT:-external_artifacts/baselines/sota_baselines_2026-04-25}"

echo "BASELINE_ROOT=$BASELINE_ROOT"
echo "HOST=$(hostname)"
echo "DATE_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "== GPU =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
else
  echo "nvidia-smi not found"
fi

echo "== Repos =="
for repo in convolutional_occupancy_networks occupancy_networks nksr POCO; do
  if [ -d "$BASELINE_ROOT/repos/$repo/.git" ]; then
    printf '%s\t' "$repo"
    git -C "$BASELINE_ROOT/repos/$repo" rev-parse --short HEAD
  else
    echo "$repo missing"
  fi
done

echo "== Manifests =="
find "$BASELINE_ROOT/data_manifests" -maxdepth 1 -type f -printf '%f %s bytes\n' 2>/dev/null || true

echo "== Status =="
if [ -f "$BASELINE_ROOT/deploy_status.json" ]; then
  cat "$BASELINE_ROOT/deploy_status.json"
else
  echo "deploy_status.json missing"
fi


