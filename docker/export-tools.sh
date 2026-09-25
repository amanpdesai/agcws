#!/usr/bin/env bash
# Export committed source, not dirty worktrees, into a fresh build context.
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
. "$repo_root/tools/tools.lock"
destination=${1:?Usage: bash docker/export-tools.sh NEW_DIRECTORY}
[[ ! -e "$destination" ]] || { echo 'Export directory already exists' >&2; exit 2; }
mkdir -p "$destination"

export_source() {
  local source=$1 revision=$2 output=$3 recursive=$4
  local mode kind hash path
  [[ $(git -C "$source" rev-parse HEAD) == "$revision" ]] || {
    echo "Wrong checkout at $source. Run bash tools/setup.sh." >&2
    return 2
  }
  mkdir -p "$output"
  git -C "$source" archive "$revision" | tar -xf - -C "$output"
  printf '%s %s\n' "${source#"$repo_root/"}" "$revision" >> "$destination/revisions.txt"
  if [[ "$recursive" == yes ]]; then
    while read -r mode kind hash path; do
      [[ "$kind" == commit ]] || continue
      export_source "$source/$path" "$hash" "$output/$path" yes
    done < <(git -C "$source" ls-tree -r "$revision")
  fi
}

# CHIA's nested submodules are examples, not Python package dependencies.
export_source "$repo_root/tools/chia" "$CHIA_REF" "$destination/chia" no
export_source "$repo_root/tools/opensta" "$OPENSTA_REF" "$destination/opensta" yes
export_source "$repo_root/tools/yosys" "$YOSYS_REF" "$destination/yosys" yes
export_source "$repo_root/tools/iverilog" "$IVERILOG_REF" "$destination/iverilog" yes
export_source "$repo_root/tools/verilator" "$VERILATOR_REF" "$destination/verilator" yes
export_source "$repo_root/tools/sv-elab" "$SV_ELAB_REF" "$destination/sv-elab" yes
export_source "$repo_root/tools/cudd" "$CUDD_REF" "$destination/cudd" yes
export_source "$repo_root/tools/boost-regex" "$BOOST_REGEX_REF" "$destination/boost-regex" yes
