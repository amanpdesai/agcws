# Temporal scaling v1 — CPU qualification

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

This is a bounded engineering qualification, not a policy-efficacy study.
It is complete: twelve witness proposals and 72 search slots; the independent
audit passes. See [findings](../../RESULTS.md).
The manifest and source snapshots were committed before execution. Completion
requires `complete.json`, `summary.json` and a passing independent archive audit.

Protocol: [temporal scaling plan](../../archive/README.md).
12 witness proposals; first two valid nonflat achieved profiles; 72 search slots
across legacy-random, phase-random and phase-GA; no model calls. The 25 request
examples include durations/resolutions unsupported by the unchanged evaluator.
Those requests must not be presented as feasible measured benchmarks.

Run and archive:

```bash
python -m experiments.temporal_scaling_v1.smoke run --root out/temporal-scaling-v1 --archive results/temporal_scaling_v1
python -m experiments.temporal_scaling_v1.smoke archive --root out/temporal-scaling-v1 --archive results/temporal_scaling_v1
python -m analysis.temporal_scaling_v1 --archive results/temporal_scaling_v1
```

Generate a request (the output must not already exist):

```bash
python -m experiments.temporal_scaling_v1.targets --seed 901 --family random_steps --phases 8 --horizon-cycles 800000 --bins 32 --out out/request-800k-32bins.json
```

This only writes a desired shape. It does not run a longer simulation or assert
that an achievable program exists. Witness programs in this archive are for
offline verification only; do not pass this directory to a search controller.
