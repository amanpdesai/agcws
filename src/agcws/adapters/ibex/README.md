# Ibex adapter

This adapter defines the instruction-stream workload boundary for Ibex. A
workload contains a program of structured instructions, with legal load/store
addresses, aligned branch targets, supported instruction names, and an `ecall`
termination point. `useful_work` is the retired-instruction count supplied by
the future simulator harness.

`scripts/compile_ibex_workload.py` deterministically lowers this DSL to RV32IM
assembly and an ELF image for Ibex's upstream `ibex_simple_system`. The image
uses the system's documented 1 MiB RAM map and simulator-halt register. The
compiler is intentionally separate from the adapter so policies still operate
on structured JSON, while the container owns the compiler toolchain.

`scripts/run_ibex_workload.sh` runs the generated ELF with the upstream
Verilator simulator and collects retirement counters, the core trace, and an
FST waveform into one output directory. Gate-level power integration remains a
separate validation step.
