#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
out_dir=${1:-out/aes-core-synthesis}
liberty=${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
yosys_bin=${AGCWS_YOSYS:-yosys}
# The host may contain a plugin built against a different Yosys ABI. Keep the
# compatibility frontend as the reproducible default; opt in explicitly only
# after checking the plugin against the selected Yosys binary.
slang_plugin=${AGCWS_SLANG_PLUGIN:-}
memory_libmap=${AGCWS_MEMORY_LIBMAP:-}
memory_manifest=${AGCWS_MEMORY_MANIFEST:-}
mkdir -p "$out_dir"

memory_pass="memory_map"
if [[ -n "$memory_libmap" ]]; then
  test -f "$memory_libmap" || { echo "missing AGCWS_MEMORY_LIBMAP: $memory_libmap" >&2; exit 2; }
  test -f "$memory_manifest" || { echo "set AGCWS_MEMORY_MANIFEST" >&2; exit 2; }
  python3 - "$memory_manifest" <<'PY'
import json
import sys
manifest = json.load(open(sys.argv[1], encoding="utf-8"))
if manifest.get("mapping_policy") != "map_eligible_flatten_incompatible":
    raise SystemExit("memory collateral lacks the mixed mapping/flatten policy")
PY
  memory_pass="memory_libmap -lib $memory_libmap; memory_map"
fi

python3 scripts/resolve_sv_sources.py --top aes_cipher_core > "$out_dir/sources.list"
mapfile -t sources < "$out_dir/sources.list"

if [[ -n "$slang_plugin" && -f "$slang_plugin" ]]; then
  frontend="plugin -i $slang_plugin; read_slang --top aes_cipher_core -D SYNTHESIS -I third_party/opentitan/hw/ip/aes/rtl -I third_party/opentitan/hw/ip/prim/rtl -I third_party/opentitan/hw/ip/prim_generic/rtl -I third_party/opentitan/hw/ip/edn/rtl -I third_party/opentitan/hw/ip/csrng/rtl -I third_party/opentitan/hw/ip/entropy_src/rtl ${sources[*]}"
else
  echo "using Yosys compatibility frontend (set AGCWS_SLANG_PLUGIN to opt in)" >&2
  compat_dir="$out_dir/frontend_compat"
  mkdir -p "$compat_dir"
  compat_sources=()
  for source in "${sources[@]}"; do
    target="$compat_dir/$(basename "$source")"
    python3 scripts/yosys_sv_compat.py "$source" "$target"
    compat_sources+=("$target")
  done
  frontend="read_verilog -sv -DSYNTHESIS ${compat_sources[*]}"
fi

"$yosys_bin" -Q -T -p "\
$frontend; \
hierarchy -top aes_cipher_core; \
proc; opt; $memory_pass; opt; \
techmap; opt; \
dfflibmap -liberty $liberty; \
abc -liberty $liberty; \
clean; \
write_verilog -noattr -noexpr $out_dir/mapped.v; \
tee -o $out_dir/stat.json stat -liberty $liberty -json" \
  > "$out_dir/yosys.log" 2>&1

sha256sum "$out_dir/mapped.v" | awk '{print $1}' > "$out_dir/netlist.sha256"
sha256sum "$liberty" | awk '{print $1}' > "$out_dir/liberty.sha256"
sha256sum "${sources[@]}" | sha256sum | awk '{print $1}' > "$out_dir/sources.sha256"
python3 - "$out_dir/manifest.json" "$liberty" "$out_dir" "$frontend" "$yosys_bin" "$slang_plugin" "$memory_libmap" "$memory_manifest" <<'PY'
import json
import sys
from pathlib import Path

manifest, liberty, out_dir, frontend, yosys_bin, slang_plugin, memory_libmap, memory_manifest = sys.argv[1:]
root = Path(out_dir)
import subprocess
version = subprocess.run([yosys_bin, "-V"], capture_output=True, text=True, check=True).stdout.strip()
memory_sha256 = None
memory_manifest_sha256 = None
if memory_libmap:
    import hashlib
    memory_sha256 = hashlib.sha256(Path(memory_libmap).read_bytes()).hexdigest()
    memory_manifest_sha256 = hashlib.sha256(Path(memory_manifest).read_bytes()).hexdigest()
Path(manifest).write_text(json.dumps({
    "top": "aes_cipher_core",
    "liberty": liberty,
    "netlist_sha256": (root / "netlist.sha256").read_text().strip(),
    "liberty_sha256": (root / "liberty.sha256").read_text().strip(),
    "sources_sha256": (root / "sources.sha256").read_text().strip(),
    "frontend": "slang" if frontend.startswith("plugin -i") else "yosys-compat",
    "yosys_version": version,
    "slang_plugin": slang_plugin or None,
    "memory_libmap": memory_libmap or None,
    "memory_libmap_sha256": memory_sha256,
    "memory_manifest": memory_manifest or None,
    "memory_manifest_sha256": memory_manifest_sha256,
}, indent=2) + "\n")
PY
echo "SYNTHESIS_DONE out=$out_dir"
