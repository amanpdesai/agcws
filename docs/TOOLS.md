# Tools and dependencies

Executable tools belong in the Docker image; framework, RTL and baseline source
are pinned dependencies. Libraries are checked into `third_party/liberty/`.
Exact study versions and checksums are recorded in the frozen manifests, not
in mutable prose defaults. [RESULTS.md](../RESULTS.md) records current findings.

| Component | Purpose | Configuration |
|---|---|---|
| Python, NumPy, google-genai | Controller, baselines, accounting | `make install`; `pyproject.toml` |
| CHIA / Ray | Composable hardware tasks | `tools/chia`, `make chia-install` |
| Docker | Isolated reusable EDA environment | `docker/build.sh`, `docker/run.sh` |
| Verilator | RTL simulation and activity | `AGCWS_VERILATOR` |
| Yosys / Slang | Elaboration and cached mapping | `AGCWS_YOSYS`, `AGCWS_SLANG_PLUGIN` |
| OpenSTA | Full-span and native-window gate power | `AGCWS_OPENSTA` |
| Icarus + cell models | Mapped-netlist simulation | `AGCWS_IVERILOG`, `AGCWS_VVP`, cell-model settings |
| RISC-V GCC / binutils | Ibex program compilation | Container toolchain; host `.env` overrides |
| FuseSoC | Ibex source and simulator preparation | `AGCWS_FUSESOC` |
| bsg_fakeram | Compatible memory collateral | Pinned `third_party/bsg_fakeram` |
| Sky130 HD / Nangate45 | Characterized cell power | `AGCWS_LIBERTY`, `AGCWS_LIBERTY_NANGATE45` |
| GeST source | Qualified evolutionary operators | Pinned third-party source; hash-checked bridge |

The pipeline pins the resolved Docker image digest and simulator binary hash.
Host-specific paths stay in `.env`; no credentials enter source or exports.
Vertex preflight (`make vertex-preflight`) makes no paid request. Frozen model
arms are explicit in the pipeline; changing `.env` does not silently replace a
prepared model. A model change requires a new study configuration/protocol.

See [OpenSTA provenance](OPENSTA_UPSTREAM.md), [stage scripts](../scripts/README.md)
and [pipeline usage](PIPELINE.md). Memory geometry alone is not characterization:
unsupported interfaces remain explicitly unmapped; fake power is never accepted.
No GitHub CI, global Docker prune, or automatic experiment launch is configured.
