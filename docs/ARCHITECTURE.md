# Architecture

## Prime directive

`nodes/` are generic and copyable into CHIA. `adapters/` know one design. `flows/` wire nodes. `experiments/` contain disposable drivers and sweeps. `analysis/` reads results and writes figures.

## Layout

```text
agcws/{docs,tools/chia,src/agcws/{nodes,adapters,goals,policies,telemetry},flows,experiments,analysis,docker}
```

`DesignAdapter` validates schema/protocol/functionality, elaborates DSL workloads, reports useful work, and exposes optional synthesis regions. Every `SearchPolicy` uses the same DSL, legality checker, history, and evaluator budget.

Validity is a four-stage hard gate: SCHEMA → PROTOCOL → FUNCTIONAL → USEFUL WORK. Invalid workloads receive no power score. The currently frozen useful-work floors are AES ≥38 blocks, `axi_dma` ≥4096 completed bytes, and Ibex ≥10,000 retired instructions; these are derived from the Slice-4 corpus and must change only through `DECISIONS.md`. The scalar AES tolerance is frozen at ε=0.05 envelope-normalized units under the declared calibration rule.

`ActivityEvaluator` is the inner loop (Verilator → VCD/FST → switching estimate); `SynthesisEvaluator` validates finalists (Yosys → mapped netlist → OpenSTA). Activity artifacts retain per-cycle and coarse-window toggle counts plus the SHA-256 of the source waveform. Every profile records fidelity and provenance. Seeds, model/temperature, tools, Liberty, container digest, timing, tokens, cost, validity, workload, and profile are recorded per trial.
