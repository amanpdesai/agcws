# Tools

## Setup

```bash
bash tools/setup.sh
cp .env.example .env
make install
.venv/bin/python -m agcws doctor
```

Keep host paths in ignored `.env` and Google credentials in ADC. Study manifests
record the actual tool versions, images and model settings. Editing `.env` does
not replace a frozen study configuration.

## Dependencies

[tools/](../tools/) contains source submodules for CHIA, OpenSTA, Yosys, Icarus,
Verilator, sv-elab, CUDD and Boost.Regex. Nested ABC, Slang and fmt sources are
pinned by their parent repositories. [tools.lock](../tools/tools.lock) records
matching commits, build dependencies and Python hardware tool versions.

Use `tools/setup.sh` instead of recursive cloning. It initializes the pinned
dependencies while skipping CHIA's unused example repositories.

The Docker wrapper exports committed source from these checkouts, including
nested dependencies. It never copies local edits or clones tool repositories
inside the image. CHIA's optional example submodules are not part of its package
export. Source builds of Yosys 0.52 and Icarus 12.0 replace the Debian packages
in new images only. Base Verilator remains the pinned Debian 5.032 package,
while the benchmark layer builds the pinned Verilator submodule.

These pins describe the next build, not a replacement for frozen study runtimes.
Debian transitive dependencies and the broader Python application environment
are not fully locked. Removed package versions cause a build failure rather than
an automatic upgrade. A fresh image still requires build and smoke verification.

| Tool | Purpose | Configuration |
|---|---|---|
| Python and NumPy | Runner and classical search | `pyproject.toml`, `make install` |
| google-genai | Model API requests | Research dependencies and ADC |
| CHIA and Ray | Framework integration | Pinned `tools/chia` |
| Docker | EDA environment | `docker/build.sh`, `docker/run.sh` |
| Verilator | RTL simulation | `AGCWS_VERILATOR` |
| Icarus | DMA RTL and gate simulation | `AGCWS_IVERILOG`, `AGCWS_VVP` |
| Yosys and Slang | Elaboration and synthesis | `AGCWS_YOSYS`, `AGCWS_SLANG_PLUGIN` |
| OpenSTA | Internal and switching power estimates | `AGCWS_OPENSTA` |
| RISC-V GCC and FuseSoC | Ibex programs and builds | Container toolchain, `AGCWS_FUSESOC` |
| Sky130 HD and Nangate45 | Cell characterization | `AGCWS_LIBERTY`, `AGCWS_LIBERTY_NANGATE45` |
| bsg_fakeram | Memory models | Pinned `benchmarks/support/bsg_fakeram` |
| GeST | Evolutionary search support | Pinned `tools/baseline-references/gest` |
| zstd and fst2vcd | Waveform compression and conversion | Host `zstd` and `gtkwave` packages |

Use the library and memory models recorded for the selected design, not an
interchangeable default. See [Docker setup](../docker/README.md) for image use.

## OpenSTA

The lock and window-power implementation pin upstream commit
`a9a3f30ca97dc13f9ef911cae1a82c42c67379e1`. Set `AGCWS_OPENSTA` to the absolute
path of the corresponding `sta` executable. Preserve an active installation
under `out/tools/` until a verified replacement is available.

The verification entry point is
`python -m agcws.evaluation.power.verify_windows --help`.

OpenSTA's `read_vcd -begin_time/-end_time` uses integer ticks from the VCD's own
timescale. Endpoints are inclusive. The window evaluator places internal cuts
at event-free timestamps, checks RTL/gate alignment and starts a fresh OpenSTA
process for each window. Do not substitute nanoseconds for VCD ticks or reuse
stale activity across reads.

For archived studies, use their recorded tool identities and frozen runtime.
See [architecture and workflow](ARCHITECTURE.md) for the execution stages.
