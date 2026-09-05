#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
task_uid=$(id -u)
task_gid=$(id -g)
artifact_dir=${AGCWS_CONTAINER_OUTPUT:-$repo_root/out/container-runs/$task_uid}
mkdir -p "$artifact_dir"
artifact_dir=$(realpath "$artifact_dir")
if [[ "$artifact_dir" == / || "$artifact_dir" == "$repo_root" ]]; then
  echo 'artifact directory must not be / or the checkout root' >&2
  exit 2
fi
if [[ $# -eq 0 ]]; then
  set -- python3 -c 'import agcws; print(agcws.__version__)'
fi
exec docker run --rm --init --read-only --user "$task_uid:$task_gid" \
  --label io.agcws.project=agcws --label "io.agcws.owner=$task_uid" \
  --cap-drop ALL \
  --log-driver local --log-opt max-size=10m --log-opt max-file=3 \
  --tmpfs "/tmp:rw,exec,nosuid,nodev,size=${AGCWS_CONTAINER_TMPFS_SIZE:-8g}" \
  --mount "type=bind,src=$repo_root,dst=/workspace,readonly" \
  --mount "type=bind,src=$artifact_dir,dst=/workspace/out" --workdir /workspace \
  --env PYTHONPATH=/workspace/src --env PYTHONDONTWRITEBYTECODE=1 \
  --env AGCWS_ARTIFACT_ROOT=/workspace/out --env AGCWS_PYTHON=python3 \
  --env VENV_PYTHON=python3 "${AGCWS_CONTAINER_IMAGE:-agcws:dev}" "$@"
