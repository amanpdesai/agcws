#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
artifact_root=${AGCWS_ARTIFACT_ROOT:-out}
python_bin=${AGCWS_PYTHON:-python3}

"$python_bin" -m agcws doctor
for tool in "${AGCWS_VERILATOR:-verilator}" "${AGCWS_YOSYS:-yosys}" \
            "${AGCWS_OPENSTA:-sta}" "${AGCWS_IVERILOG:-iverilog}" \
            "${AGCWS_FST2VCD:-fst2vcd}"; do
  command -v "$tool" >/dev/null
done
"${AGCWS_OPENSTA:-sta}" -version >/dev/null
if [[ -n ${AGCWS_SLANG_PLUGIN:-} ]]; then
  "${AGCWS_YOSYS:-yosys}" -Q -p "plugin -i $AGCWS_SLANG_PLUGIN; help read_slang" >/dev/null
fi
for liberty in "${AGCWS_LIBERTY:?primary Liberty required}" \
               "${AGCWS_LIBERTY_NANGATE45:?secondary Liberty required}"; do
  "$python_bin" -m agcws.evaluation.synthesis.liberty "$liberty" >/dev/null
done
smoke_input=$("$python_bin" -c 'from importlib.resources import files; print(files("agcws.designs.dma").joinpath("assets/smoke.json"))')
AGCWS_PYTHON="$python_bin" "$python_bin" -m agcws.designs.dma.simulate \
  "$smoke_input" "$artifact_root/container-dma-smoke"
echo AGCWS_CONTAINER_SMOKE_OK
