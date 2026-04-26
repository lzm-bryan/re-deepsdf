#!/usr/bin/env bash
set -euo pipefail

BASELINE_ROOT="${BASELINE_ROOT:-external_artifacts/baselines/sota_baselines_2026-04-25}"
INSTALL_ENVS="${INSTALL_ENVS:-0}"
PYTHON_BIN="${PYTHON_BIN:-external_artifacts/runtime/deepsdf_modern/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

mkdir -p "$BASELINE_ROOT"/{docs,envs,scripts,repos,data_manifests,runs,logs}

log="$BASELINE_ROOT/logs/bootstrap_$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee -a "$log") 2>&1

echo "BASELINE_ROOT=$BASELINE_ROOT"
echo "INSTALL_ENVS=$INSTALL_ENVS"
echo "START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

clone_repo() {
  local name="$1"
  local url="$2"
  local dst="$BASELINE_ROOT/repos/$name"
  if [ -d "$dst/.git" ]; then
    echo "repo_exists $name $dst"
    git -C "$dst" rev-parse --short HEAD || true
    return 0
  fi
  echo "clone_start $name $url"
  git clone --depth 1 "$url" "$dst"
  git -C "$dst" rev-parse --short HEAD || true
}

clone_repo "convolutional_occupancy_networks" "https://github.com/autonomousvision/convolutional_occupancy_networks.git" || echo "clone_failed convonet"
clone_repo "occupancy_networks" "https://github.com/autonomousvision/occupancy_networks.git" || echo "clone_failed occupancy_networks"
clone_repo "nksr" "https://github.com/nv-tlabs/nksr.git" || echo "clone_failed nksr"
clone_repo "POCO" "https://github.com/valeoai/POCO.git" || echo "clone_failed poco"

if [ "$INSTALL_ENVS" = "1" ]; then
  if command -v conda >/dev/null 2>&1; then
    echo "conda_found $(command -v conda)"
    for env_file in "$BASELINE_ROOT"/envs/*_environment.yml; do
      [ -f "$env_file" ] || continue
      echo "conda_env_update $env_file"
      conda env update -f "$env_file" --prune || echo "conda_env_failed $env_file"
    done
  else
    echo "conda_not_found"
  fi
else
  echo "env_install_skipped"
fi

"$PYTHON_BIN" "$BASELINE_ROOT/scripts/make_input_manifests.py" \
  --workspace external_artifacts/remote_deepsdf_setup \
  --output "$BASELINE_ROOT/data_manifests" || echo "manifest_generation_failed"

"$PYTHON_BIN" - <<PY
import json, os, subprocess, time
root = os.environ.get("BASELINE_ROOT", "$BASELINE_ROOT")
repos = {}
for name in ["convolutional_occupancy_networks", "occupancy_networks", "nksr", "POCO"]:
    path = os.path.join(root, "repos", name)
    sha = None
    if os.path.isdir(os.path.join(path, ".git")):
        try:
            sha = subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip()
        except Exception:
            sha = "unknown"
    repos[name] = {"path": path, "present": os.path.isdir(path), "sha": sha}
status = {
    "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "baseline_root": root,
    "install_envs": os.environ.get("INSTALL_ENVS", "$INSTALL_ENVS"),
    "repos": repos,
}
with open(os.path.join(root, "deploy_status.json"), "w", encoding="utf-8") as f:
    json.dump(status, f, indent=2)
print(json.dumps(status, indent=2))
PY

echo "DONE_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"


