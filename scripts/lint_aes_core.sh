#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
sources=$(mktemp)
trap 'rm -f "$sources"' EXIT
python3 scripts/resolve_sv_sources.py --top aes_cipher_core > "$sources"

verilator --lint-only --sv --top-module aes_cipher_core -DSYNTHESIS \
  -Ithird_party/opentitan/hw/ip/aes/rtl \
  -Ithird_party/opentitan/hw/ip/prim/rtl \
  -Ithird_party/opentitan/hw/ip/prim_generic/rtl \
  -Ithird_party/opentitan/hw/ip/edn/rtl \
  -Ithird_party/opentitan/hw/ip/csrng/rtl \
  -Ithird_party/opentitan/hw/ip/entropy_src/rtl \
  $(<"$sources")
