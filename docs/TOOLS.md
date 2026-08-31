# Tool and dependency inventory

This project does **not** make executables Git submodules. Source dependencies
are pinned as submodules; executable tools are version-checked on the host and
ultimately pinned in the container image.

## Required for Slice 1

| Dependency | Role | Current state | Reproducibility plan |
|---|---|---|---|
| Python 3.10.19 | CHIA runtime | Inspect/install | Container + lockfile |
| `uv` | Python environment management | Installed | Pin in setup docs |
| Ray 2.54.0 | CHIA execution substrate | Via CHIA environment | Python lockfile |
| Docker | CHIA worker/tool environments | Installed | Pin image digest |
| Git/GitHub CLI | source, auth, submodules | Installed | Host prerequisite |
| Vertex AI Gemini | agent calls | Not configured in repo | Credentials outside Git; exact model recorded per trial |

## Required for Slice 2

| Tool | Role | Current state | Reproducibility plan |
|---|---|---|---|
| Verilator | RTL simulation and VCD/FST tracing | Set by `AGCWS_VERILATOR` | Container image/version |
| Yosys | RTL synthesis/mapping | Set by `AGCWS_YOSYS` | Container image/version |
| OpenSTA (`sta`) | synthesis-level timing/power report | Set by `AGCWS_OPENSTA` | Container image/version |
| Liberty library | cell power/timing characterization | Copied into `third_party/liberty/`; selected by `AGCWS_LIBERTY` | Store path/checksum in provenance; inspect before claims |
| Icarus Verilog | small smoke tests | `/usr/bin/iverilog` | Optional fallback, not power oracle |
| Matplotlib | deterministic activity figures | Optional analysis extra | Install with `make analysis-install` |
| MyHDL + Icarus VPI | upstream verilog-axi coupled-DMA reference test | Optional verification extra | Run `make upstream-dma-reference` |

## Source dependencies to pin as submodules

Only design/framework source belongs here: `tools/chia` is pinned at
`d78ad77e4ce7b11523bf15a253a258c0f8795673`; OpenTitan is pinned at
`b16f2be75d2f38c62d861208453ed5b81ccf41b0`; verilog-axi is pinned at
`516bd5dadc3365b7f9e225d2af8fe0b8d804fe53`; and Ibex is pinned at
`8b8ee086aef72e0833b7f0493d9d33f1e4d3c8e2`. Do not vendor their trees into
this repository.

The upstream verilog-axi MyHDL testbenches are reference material only and are
not part of the AGCWS runtime dependency set. Project-owned DMA smoke tests
use native Icarus/SystemVerilog harnesses so the container remains smaller and
the required toolchain is explicit.
The optional `make upstream-dma-reference` target runs the upstream coupled
DMA test in an isolated temporary checkout and writes a hash-bearing reference
manifest plus test log under `out/axi-dma-upstream-reference/`; generated VPI,
VVP, and waveform artifacts in the temporary checkout are removed on exit.

Liberty files are the exception: selected Sky130 HD TT and Nangate45 typical
files are copied into `third_party/liberty/` so runs do not depend on a machine
path. Their source paths and checksums are recorded there.

## Not required yet

GTKWave is useful for debugging but not required for automated runs. FireSim,
commercial PDKs, commercial power tools, and FPGA toolchains are out of scope.

## Setup acceptance checks

The Slice-1 setup is ready when CHIA imports, Ray starts, Docker runs a worker,
and one stock CHIA case completes. Slice 2 additionally requires a Verilator
trace, Yosys mapped netlist, Liberty inspection, and OpenSTA power report.

The checked-in Liberty inputs are inspected with `scripts/inspect_liberty.py`.
The complete AES vertical-slice acceptance check is `make research-smoke`; it
reuses an existing synthesis manifest and produces evaluation, determinism,
and activity-figure artifacts under `out/research-smoke/`.
The script honors `AGCWS_PYTHON` for container or alternate-environment use;
the Make target defaults it to the project virtualenv.

Host configuration is optional and comes from an untracked `.env` copied from
`.env.example`. Relative paths are repository-relative. The container supplies
its own defaults, so host-specific `/opt/eda` paths do not enter the artifact.
The Yosys-slang frontend is opt-in via `AGCWS_SLANG_PLUGIN`; the default
compatibility frontend avoids host-specific Yosys plugin ABI mismatches.

For local CHIA development, run `make chia-install` after `make dev-install`.
This installs the pinned checkout and its Ray/Vertex dependencies into the
project virtual environment; the lightweight default development install does
not pull those large runtime dependencies.
Run `make chia-smoke` to verify the installed CHIA package, CLI import path, and
local Ray task execution. This is the local acceptance check; the upstream stock
case and Vertex billing confirmation remain environment-specific Slice-1 gates.
The primary Sky130 file is the default; Nangate45 is used for finalist
cross-checks. `scripts/aes_sources.py` emits the current OpenTitan AES RTL set.
`scripts/lint_aes_core.sh` is the first executable RTL acceptance check.
