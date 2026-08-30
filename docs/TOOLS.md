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
| Liberty library | cell power/timing characterization | Set by `AGCWS_LIBERTY`; initial candidate is the local Sky130 HD TT library | Store path/checksum in provenance; do not assume completeness |
| Icarus Verilog | small smoke tests | `/usr/bin/iverilog` | Optional fallback, not power oracle |

## Source dependencies to pin as submodules

Only design/framework source belongs here: `tools/chia` is pinned at
`d78ad77e4ce7b11523bf15a253a258c0f8795673`. Later add pinned commits for
OpenTitan AES, verilog-axi `axi_dma`, and Ibex after selecting the exact RTL
versions. Do not vendor their trees into this repository.

## Not required yet

GTKWave is useful for debugging but not required for automated runs. FireSim,
commercial PDKs, commercial power tools, and FPGA toolchains are out of scope.

## Setup acceptance checks

The Slice-1 setup is ready when CHIA imports, Ray starts, Docker runs a worker,
and one stock CHIA case completes. Slice 2 additionally requires a Verilator
trace, Yosys mapped netlist, Liberty inspection, and OpenSTA power report.
