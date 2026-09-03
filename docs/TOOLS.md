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
| RISC-V GCC + binutils | Ibex instruction-image assembly/linking | Container-provided (`riscv64-unknown-elf-*`) | Record compiler version in workload provenance |
| bsg_fakeram | Generate capability-aware SRAM Verilog/LEF/Liberty views from explicit characterization | Pinned submodule at `639fb69d8cbf8c956592615386429413b1230fbb` | Build its pinned CACTI dependency only when macro generation is enabled |

## Source dependencies to pin as submodules

Only design/framework source belongs here: `tools/chia` is pinned at
`d78ad77e4ce7b11523bf15a253a258c0f8795673`; OpenTitan is pinned at
`b16f2be75d2f38c62d861208453ed5b81ccf41b0`; verilog-axi is pinned at
`516bd5dadc3365b7f9e225d2af8fe0b8d804fe53`; Ibex is pinned at
`8b8ee086aef72e0833b7f0493d9d33f1e4d3c8e2`; and bsg_fakeram is pinned at
`639fb69d8cbf8c956592615386429413b1230fbb`. Do not vendor their trees into
this repository.

The upstream verilog-axi MyHDL testbenches are reference material only and are
not part of the AGCWS runtime dependency set. Project-owned DMA smoke tests
use native Icarus/SystemVerilog harnesses so the container remains smaller and
the required toolchain is explicit.
The optional `make upstream-dma-reference` target runs the upstream coupled
DMA test in an isolated temporary checkout and writes a hash-bearing reference
manifest plus test log under `out/axi-dma-upstream-reference/`; generated VPI,
VVP, and waveform artifacts in the temporary checkout are removed on exit.
The script honors `AGCWS_PYTHON`, defaulting to `.venv/bin/python`.

Memory-aware synthesis uses Yosys `memory -nomap` inventory first, then emits
the native bsg_fakeram JSON configuration under `out/memory-collateral/`.
The generator is intentionally not run as part of ordinary verification: its
CACTI build is expensive and generated macro models must be reviewed for port
latency and Liberty compatibility before they can replace flop mapping.
After generating the design bundles, `make audit-memory-collateral-all`
audits AES, AXI DMA, and Ibex together. A valid audit may report
`mapping_ready: false`: that is the expected, explicit result while a design's
memory port semantics lack a verified compatible macro backend.

`make verify-artifact AGCWS_ARTIFACT=out/aes-evaluation` checks a result bundle's
validity, useful-work field, and recorded input SHA-256 hashes. Run it after
copying or archiving results to catch stale or modified inputs before analysis.

Liberty files are the exception: selected Sky130 HD TT and Nangate45 typical
files are copied into `third_party/liberty/` so runs do not depend on a machine
path. Their source paths and checksums are recorded there.

## Not required yet

GTKWave is useful for debugging but not required for automated runs. FireSim,
commercial PDKs, commercial power tools, and FPGA toolchains are out of scope.

## Setup acceptance checks

The Slice-1 setup is ready when CHIA imports, Ray starts, Docker runs a worker,
and one stock CHIA case completes. The container smoke includes the local
CHIA/Ray task check as well as the EDA checks. Slice 2 additionally requires a Verilator
trace, Yosys mapped netlist, Liberty inspection, and OpenSTA power report.

The checked-in Liberty inputs are inspected with `make inspect-liberties`, which
reports characterization features and SHA-256 digests for both Sky130 and
Nangate45. `make inspect-liberty` remains available for the primary library.
The complete AES vertical-slice acceptance check is `make research-smoke`; it
reuses an existing synthesis manifest and produces scalar evaluation,
determinism, activity-figure, temporal-search, and compositional-search
artifacts under `out/research-smoke/`. Set `AGCWS_PROFILE_SMOKE_BUDGET` to
change the small profile smoke budget without changing comparative budgets.
The resulting `activity.json` includes the waveform SHA-256 alongside the
per-cycle, coarse-window, and max-normalized window counts. The normalized
profile is derived from the same window buckets used by temporal goals; an
all-zero profile remains all zero. The script honors `AGCWS_PYTHON` for container or alternate-environment use;
the Make target defaults it to the project virtualenv.

Host configuration is optional and comes from an untracked `.env` copied from
`.env.example`. Relative paths are repository-relative. The container supplies
its own defaults, so host-specific `/opt/eda` paths do not enter the artifact.
The Yosys-slang frontend is opt-in via `AGCWS_SLANG_PLUGIN`; the default
compatibility frontend avoids host-specific Yosys plugin ABI mismatches.
The AES GLS probe is `scripts/run_aes_gls.sh`; it requires explicit Sky130
functional and primitive cell models and is separate from RTL-VCD annotation.
It emits a VCD from the mapped netlist itself. Pass
`AGCWS_VCD_SCOPE=aes_core_gls/dut` to `scripts/run_opensta_aes.sh` when reading
that waveform; the resulting OpenSTA report is the gate-level evaluator tier.

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
`make vertex-preflight` checks the non-secret Vertex project/model configuration
and frozen prompt without making an API call. `make probe-ibex-synthesis`
captures the current Ibex Slang/Yosys elaboration boundary and intentionally
fails if no valid gate-level design is produced.
