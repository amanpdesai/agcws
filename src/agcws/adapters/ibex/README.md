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

The simulator invocation and instruction-retirement extraction remain the next
bring-up step; this compiler does not claim gate-level power results by itself.
