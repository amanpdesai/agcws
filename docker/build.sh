#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
task_uid=$(id -u)
builder="agcws-$task_uid"
if ! docker buildx inspect "$builder" >/dev/null 2>&1; then
  docker buildx create --name "$builder" --driver docker-container \
    --buildkitd-config "$repo_root/docker/buildkitd.toml" >/dev/null
fi
exec docker buildx build --builder "$builder" --load \
  --label io.agcws.project=agcws --label "io.agcws.owner=$task_uid" \
  -f "$repo_root/docker/Dockerfile" -t "${AGCWS_CONTAINER_IMAGE:-agcws:dev}" \
  "$@" "$repo_root"
