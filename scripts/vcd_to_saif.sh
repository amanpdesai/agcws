#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 INPUT.vcd OUTPUT.saif" >&2
  exit 2
fi

vcd="$1"
saif="$2"
mkdir -p "$(dirname "$saif")"
"${AGCWS_VCD2SAIF:-vcd2saif}" -input "$vcd" -output "$saif"
echo "SAIF_DONE output=$saif"
