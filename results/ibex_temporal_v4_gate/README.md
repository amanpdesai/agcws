# V4 diagnostic-label CPU gate

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

One partial-iteration development program replayed twice on the pinned Ibex
simulator: unchanged v3 assembly versus the same assembly with address labels.
Loadable bytes, architectural state, observation markers, activity-bin counts,
retirement classes and completion time match exactly. `gate.json` indexes the
compact evidence hashes. Raw FST and retirement traces remain local scratch.

`annotated/execution.json` reports retirement-time phase bounds and executed
operand events. These are not instruction issue times or measured stall causes.
The evaluator cross-checks phase retirement totals and divide counts against the
independent v3 feedback extractor. This one-case gate is not a comparative agent
result or exhaustive proof for every legal program; additional readiness checks
remain necessary before the temporal panel.

Reproduction from a prepared v4 output root (contains the pinned simulator):

```bash
python -m experiments.ibex_temporal_v4.gate \
  --root out/ibex-temporal-v4 \
  --source results/ibex_temporal_v4_gate/input.json
```

The command refuses to overwrite an existing `equivalence/` directory. Use a new
prepared root to rerun it. The project has made no v4 model calls yet.
