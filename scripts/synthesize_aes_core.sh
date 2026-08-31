#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
out_dir=${1:-out/aes-core-synthesis}
liberty=${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
mkdir -p "$out_dir"

python3 scripts/resolve_sv_sources.py --top aes_cipher_core > "$out_dir/sources.list"
mapfile -t sources < "$out_dir/sources.list"

# Yosys' bundled frontend does not accept the typed enum casts used in the
# upstream package. Keep the upstream RTL untouched and make a deterministic
# frontend-compatibility copy only for synthesis. Verilator still validates the
# original sources in the simulation flow.
compat_dir="$out_dir/frontend_compat"
mkdir -p "$compat_dir"
compat_sources=()
for source in "${sources[@]}"; do
  target="$compat_dir/$(basename "$source")"
  if [[ "$source" == *"/aes_pkg.sv" ]]; then
    python3 scripts/yosys_sv_compat.py "$source" "$target"
  else
    ln -sf "$source" "$target"
  fi
  compat_sources+=("$target")
done

"${AGCWS_YOSYS:-yosys}" -Q -T -p "\
read_verilog -sv -DSYNTHESIS ${compat_sources[*]}; \
hierarchy -top aes_cipher_core; \
proc; opt; memory_map; opt; \
techmap; opt; \
dfflibmap -liberty $liberty; \
abc -liberty $liberty; \
clean; \
write_verilog -noattr -noexpr -blackbox $out_dir/mapped.v; \
stat -liberty $liberty -json > $out_dir/stat.json" \
  > "$out_dir/yosys.log" 2>&1

sha256sum "$out_dir/mapped.v" | awk '{print $1}' > "$out_dir/netlist.sha256"
sha256sum "$liberty" | awk '{print $1}' > "$out_dir/liberty.sha256"
printf '{"top":"aes_cipher_core","liberty":"%s","netlist":"%s"}\n' \
  "$liberty" "$(<"$out_dir/netlist.sha256")" > "$out_dir/manifest.json"
echo "SYNTHESIS_DONE out=$out_dir"
