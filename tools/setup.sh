#!/usr/bin/env bash
# Initialize pinned dependencies without CHIA's optional example repositories.
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
git -C "$repo_root" submodule update --init --jobs 8
git -C "$repo_root" submodule foreach --quiet '
  if [ "$sm_path" != "tools/chia" ]; then
    git submodule update --init --recursive --jobs 8
  fi
'
