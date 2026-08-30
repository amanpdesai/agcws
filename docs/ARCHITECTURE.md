# Architecture

## Prime directive

`nodes/` are generic and copyable into CHIA. `adapters/` know one design. `flows/` wire nodes. `experiments/` contain disposable drivers and sweeps. `analysis/` reads results and writes figures.

## Layout

```text
agcws/{docs,tools/chia,src/agcws/{nodes,adapters,goals,policies,telemetry},flows,experiments,analysis,docker}
```

`DesignAdapter` validates schema/protocol/functionality, elaborates DSL workloads, reports useful work, and exposes optional synthesis regions. Every `SearchPolicy` uses the same DSL, legality checker, history, and evaluator budget.

Validity is a four-stage hard gate: SCHEMA → PROTOCOL → FUNCTIONAL → USEFUL WORK. Invalid workloads receive no power score. Provisional useful-work floors are AES ≥16 blocks, `axi_dma` ≥4096 completed bytes, and Ibex ≥10,000 retired instructions; freeze them from the Slice-4 corpus.

`ActivityEvaluator` is the inner loop (Verilator → VCD/FST → switching estimate); `SynthesisEvaluator` validates finalists (Yosys → mapped netlist → OpenSTA). Every profile records fidelity and provenance. Seeds, model/temperature, tools, Liberty, container digest, timing, tokens, cost, validity, workload, and profile are recorded per trial.
