# Hardware stage commands

Study orchestration lives only in `agcws.pipeline`; see
[usage](../docs/PIPELINE.md). Historical sweeps, calibration drivers and report
generators live in the [verified source archive](../archive/README.md).
This directory retains independently useful hardware/tool stages.

| Stage | Entry points |
|---|---|
| Source closure | `resolve_ibex_sources.py`, `resolve_sv_sources.py` |
| Memory preparation | `inventory_yosys_memories.py`, `generate_memory_collateral.py`, `audit_memory_collateral.py` |
| Synthesis | `synthesize_aes_core.sh`, `synthesize_axi_dma.sh`, `probe_ibex_synthesis.py` |
| RTL simulation | `run_aes_transactions.py`, `run_axi_dma_coupled.sh`, `run_ibex_workload.sh` |
| Mapped simulation | `run_aes_gls.sh`, `run_axi_dma_gls.sh` |
| Activity extraction | `parse_vcd_activity.py`, `vcd_to_saif.sh` |
| Gate power | `run_opensta_aes.sh`, `run_opensta_axi_dma.sh` |
| Environment | `vertex_preflight.py`, `chia_smoke.py`, `container_smoke.sh` |

Commands use `.env`/explicit arguments, not machine-specific paths. Consult
Python `--help` or shell argument checks before executing. These commands can
run EDA tools; they are not invoked by `make test`, `make lint` or archive audit.

Memory collateral is generated only after reviewing dimensions, port semantics
and matching characterization. Netlist and Liberty hashes identify synthesis
cache entries. Never label contract-only memory data as power characterization.

The retained simple scalar hardware harnesses are not the maintained Ibex
phase-program study: the latter uses its own fixed-window, reference-checked
compiler and evaluator under `src/agcws/pipeline/ibex/`.
