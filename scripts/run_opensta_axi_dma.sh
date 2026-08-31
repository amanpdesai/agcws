#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 SYNTHESIS_DIR WAVEFORM.vcd [OUTPUT_DIR]" >&2
  exit 2
fi
synth_dir=$1
waveform=$2
out_dir=${3:-"$synth_dir/power"}
liberty=${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
mkdir -p "$out_dir"
cat > "$out_dir/power.tcl" <<EOF
read_liberty $liberty
read_verilog $synth_dir/mapped.v
link_design axi_dma
create_clock -name clk -period 10 [get_ports clk]
read_vcd -scope axi_dma $waveform
report_power -digits 12
report_activity_annotation -report_unannotated
EOF
"${AGCWS_OPENSTA:-sta}" -exit "$out_dir/power.tcl" > "$out_dir/power.rpt" 2>&1
awk '/^Annotated [0-9]+ pin activities\./ {print $0}' "$out_dir/power.rpt" > "$out_dir/annotation.rpt"
python3 - "$out_dir/power.rpt" "$synth_dir/manifest.json" "$out_dir/result.json" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

report, synthesis_manifest, output = map(Path, sys.argv[1:])
text = report.read_text()
match = re.search(r"^Total\s+[-+0-9.eE]+\s+[-+0-9.eE]+\s+[-+0-9.eE]+\s+(?P<power>[-+0-9.eE]+)", text, re.MULTILINE)
annotation = re.search(r"^Annotated\s+(?P<annotated>\d+) pin activities\.", text, re.MULTILINE)
unannotated = re.search(r"^unannotated\s+(?P<count>\d+)", text, re.MULTILINE)
if not match or not annotation or not unannotated:
    raise ValueError("OpenSTA report lacks total power or annotation fields")
annotated = int(annotation.group("annotated"))
unannotated_count = int(unannotated.group("count"))
output.write_text(json.dumps({
    "valid": True,
    "mean_power": float(match.group("power")),
    "fidelity": "synthesis",
    "provenance": {
        "power_metric": "opensta_total_power_w",
        "power_report": report.name,
        "power_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        "synthesis_manifest": synthesis_manifest.name,
        "annotated_pins": annotated,
        "unannotated_pins": unannotated_count,
        "annotation_fraction": annotated / (annotated + unannotated_count),
    },
}, indent=2) + "\n")
PY
echo "OPENSTA_AXI_DMA_DONE report=$out_dir/power.rpt"
