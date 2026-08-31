# Ibex adapter

This adapter defines the instruction-stream workload boundary for Ibex. A
workload contains a program of structured instructions, with legal load/store
addresses, aligned branch targets, supported instruction names, and an `ecall`
termination point. `useful_work` is the retired-instruction count supplied by
the future simulator harness.

The current implementation is a pure legality boundary; it does not claim a
working RISC-V assembler, memory model, or Ibex simulation flow. Those are
deliberately isolated as the later Ibex bring-up slice so they cannot affect
the validated AES oracle.
