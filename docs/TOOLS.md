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

## Source dependencies to pin as submodules

Only design/framework source belongs here: `tools/chia` is pinned at
`d78ad77e4ce7b11523bf15a253a258c0f8795673`. Later add pinned commits for
OpenTitan AES, verilog-axi `axi_dma`, and Ibex after selecting the exact RTL
versions. Do not vendor their trees into this repository.

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

Host configuration is optional and comes from an untracked `.env` copied from
`.env.example`. Relative paths are repository-relative. The container supplies
its own defaults, so host-specific `/opt/eda` paths do not enter the artifact.
The primary Sky130 file is the default; Nangate45 is used for finalist
cross-checks. `scripts/aes_sources.py` emits the current OpenTitan AES RTL set.
`scripts/lint_aes_core.sh` is the first executable RTL acceptance check.
