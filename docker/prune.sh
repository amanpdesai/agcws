#!/usr/bin/env bash
set -euo pipefail
if [[ $# -gt 1 || (${1:-} != '' && ${1:-} != --apply) ]]; then
  echo 'usage: bash docker/prune.sh [--apply]' >&2
  exit 2
fi
task_uid=$(id -u)
builder="agcws-$task_uid"
filters=(--filter label=io.agcws.project=agcws --filter "label=io.agcws.owner=$task_uid")
docker ps -a "${filters[@]}" --filter status=exited
docker image ls "${filters[@]}" --filter dangling=true
if [[ ${1:-} != --apply ]]; then
  echo "Preview only. --apply prunes owned stopped containers, owned dangling images,"
  echo "and unused cache older than seven days from dedicated builder $builder."
  exit 0
fi
docker container prune --force "${filters[@]}" --filter until=24h
docker image prune --force "${filters[@]}" --filter until=24h
if docker buildx inspect "$builder" >/dev/null 2>&1; then
  docker buildx prune --builder "$builder" --force --filter until=168h --reserved-space 10GB
fi
