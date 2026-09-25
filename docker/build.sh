#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
task_uid=$(id -u)
. "$repo_root/tools/tools.lock"
# Keep the literal Dockerfile base usable for direct builds, but reject drift.
grep -Fxq "FROM $BASE_IMAGE" "$repo_root/docker/Dockerfile" || {
  echo 'Dockerfile base differs from tools/tools.lock' >&2
  exit 2
}
builder="agcws-$task_uid"
mkdir -p "$repo_root/out"
tool_context_root=$(mktemp -d "$repo_root/out/tool-build-context.XXXXXXXX")
cleanup() {
  [[ "$tool_context_root" == "$repo_root"/out/tool-build-context.* ]] || return
  find "$tool_context_root" -depth -delete
}
trap cleanup EXIT
bash "$repo_root/docker/export-tools.sh" "$tool_context_root/sources"
dockerfile="$repo_root/docker/Dockerfile"
build_args=()
if [[ ${AGCWS_BUILD_VARIANT:-base} == benchmark ]]; then
  dockerfile="$repo_root/docker/benchmark.Dockerfile"
  parent=${AGCWS_BENCHMARK_BASE_IMAGE:?Set an immutable registry image@sha256:digest}
  [[ "$parent" =~ ^[^[:space:]]+@sha256:[0-9a-f]{64}$ ]] || {
    echo 'Benchmark parent must be a registry image pinned by digest' >&2
    exit 2
  }
  build_args+=(--build-arg "BASE_IMAGE=$parent")
elif [[ ${AGCWS_BUILD_VARIANT:-base} != base ]]; then
  echo 'AGCWS_BUILD_VARIANT must be base or benchmark' >&2
  exit 2
fi
if ! docker buildx inspect "$builder" >/dev/null 2>&1; then
  docker buildx create --name "$builder" --driver docker-container \
    --buildkitd-config "$repo_root/docker/buildkitd.toml" >/dev/null
fi
docker buildx build --builder "$builder" --load \
  --build-context "tool_sources=$tool_context_root/sources" \
  --label io.agcws.project=agcws --label "io.agcws.owner=$task_uid" \
  -f "$dockerfile" -t "${AGCWS_CONTAINER_IMAGE:-agcws:dev}" "${build_args[@]}" \
  "$@" "$repo_root"
