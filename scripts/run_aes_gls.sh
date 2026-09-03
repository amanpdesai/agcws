#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd); cd "$repo_root"; source scripts/load_env.sh
if [[ $# -lt 1 || $# -gt 3 ]]; then echo "usage: $0 SYNTHESIS_DIR [OUTPUT_DIR] [WORKLOAD]" >&2; exit 2; fi
synth_dir=$1; out_dir=${2:-"$synth_dir/gls"}; mkdir -p "$out_dir"
workload=${3:-}
cell_models=${AGCWS_SKY130_CELL_MODELS:-/opt/eda/ChipSTA/examples/sky130_hd.v}
primitive_models=${AGCWS_SKY130_PRIMITIVES:-/opt/eda/ChipSTA/examples/sky130_hd_primitives.v}
test -f "$cell_models" || { echo "missing AGCWS_SKY130_CELL_MODELS: $cell_models" >&2; exit 2; }
test -f "$primitive_models" || { echo "missing AGCWS_SKY130_PRIMITIVES: $primitive_models" >&2; exit 2; }
# Only package declarations are needed by the flat harness. Including the RTL
# closure here would accidentally compile a second aes_cipher_core and pull in
# assertion-only source files; the mapped netlist is the implementation under test.
mapfile -t pkg_sources < <(grep '/pkg\.sv$' "$synth_dir/sources.list")
build_dir=${AGCWS_GLS_BUILD_DIR:-out/.cache/aes-gls}; mkdir -p "$build_dir"; sim="$build_dir/aes_core_gls.vvp"
if [[ ! -x "$sim" ]]; then
  iverilog -g2012 -DFUNCTIONAL -DUNIT_DELAY= -s aes_core_gls -o "$sim" \
    "$synth_dir/mapped.v" "$cell_models" "$primitive_models" "${pkg_sources[@]}" \
    experiments/aes_core_gls.sv
fi
args=(+BLOCKS="${AGCWS_GLS_BLOCKS:-1}" +PATTERN="${AGCWS_GLS_PATTERN:-0}" +KEYLEN="${AGCWS_GLS_KEYLEN:-128}" +DECRYPT="${AGCWS_GLS_DECRYPT:-0}" +IDLE="${AGCWS_GLS_IDLE:-0}")
if [[ -n "$workload" ]]; then
  read -r blocks pattern keylen decrypt idle < <(python3 - "$workload" <<'PY'
import json, sys
w=json.load(open(sys.argv[1])); ops=w["operations"]
crypto=[o for o in ops if o.get("op") in {"encrypt","decrypt"}]
print(sum(int(o.get("blocks",1)) for o in crypto), int(w.get("data_pattern",0)), int(ops[0].get("key_len",128)), int(crypto[0].get("op")=="decrypt"), sum(int(o.get("cycles",0)) for o in ops if o.get("op")=="idle"))
PY
  )
  args=(+BLOCKS="$blocks" +PATTERN="$pattern" +KEYLEN="$keylen" +DECRYPT="$decrypt" +IDLE="$idle")
fi
(cd "$out_dir" && vvp "$repo_root/$sim" "${args[@]}") > "$out_dir/run.log" 2>&1
test -s "$out_dir/activity.vcd"
python3 scripts/parse_vcd_activity.py "$out_dir/activity.vcd" --windows 8 --output "$out_dir/activity.json"
echo "AES_GLS_DONE out=$out_dir"
