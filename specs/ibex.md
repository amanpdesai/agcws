# Ibex workload-facing design specification

This describes the pinned simple-system configuration used by this project,
not every Ibex configuration. Facts below come from source/configuration;
activity consequences are hypotheses to test, not guaranteed power behavior.

## Configuration and boundaries

- RV32MFast multiply/divide; instruction cache disabled; flip-flop register file.
  See `third_party/ibex/examples/simple_system/ibex_simple_system.core`, parameters
  `RV32M`, `ICache` and `RegFile`.
- Simple-system defaults disable the writeback stage, branch predictor,
  branch-target ALU and SecureIbex. See parameters in
  `third_party/ibex/examples/simple_system/rtl/ibex_simple_system.sv`.
- The experiment enables twelve performance counters. Extra instruction-memory
  delay is zero by default, on top of the RAM access itself. Do not invent cache
  misses, out-of-order scheduling or DRAM contention in this configuration.

## Mechanisms worth investigating

- `rtl/ibex_multdiv_fast.sv`: the `MD_IDLE` divide transition takes a shortcut for
  a zero denominator only when data-independent timing is disabled. Otherwise
  division proceeds through the normal state machine. In this configuration,
  `ibex_core.sv` derives `DataIndTiming` from disabled `SecureIbex`;
  `ibex_cs_registers.sv` disables that control when the feature is absent.
- Register updates persist. Repeated arithmetic can drive operands toward zero
  or fixed points; an instruction mnemonic alone does not determine the behavior
  of a long repeated sequence. Inspect operand selection and write dependencies.
- `rtl/ibex_load_store_unit.sv` and the simple-system memory connections define
  actual memory behavior. Workload memory accesses are confined to the compiler's
  64-word data region; aliases arise from the low six address-index bits.
- `rtl/ibex_decoder.sv`, `ibex_id_stage.sv` and `ibex_controller.sv` explain decode,
  execution and control. The workload's `cmovz` is compiled into a conditional
  branch and move; it is not a dedicated custom hardware instruction.

## Workload and measurement contract

The complete JSON Schema is authoritative for operations and parameters. In v2,
relative segment weights allocate exactly 4,096 semantic operations; a segment
executes whole body iterations plus a final prefix. Registers and memory persist
across segments. Release times are earliest start times, not deadlines: completed
work can delay subsequent segments. Waiting is active CSR/branch polling, not sleep.

All work must complete in the fixed 200,000-cycle observation. Eight equal bins
measure core bit transitions, not watts. Initialization and result printing are
excluded. The scope excludes the clock and CSR-register subtree, but other signal
copies can remain. It excludes physical RAM/register-file activity outside the
selected core hierarchy. Lower retirement rate need not imply lower power.

The evaluator is read-only and all final registers/memory are reference-checked.
Never modify RTL, testbench, accounting, reference state or observation boundaries.
