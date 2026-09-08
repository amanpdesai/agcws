# Ibex depth v1 — 16-slot panel archived; deeper prefixes running

48 closed-loop development trajectories: four targets × seeds 610–612 ×
Pro-4096, Flash-4096, random and behavior-coverage. Each runs to 128 proposals;
16/64/128 results are prefixes, not independently resampled runs. Total: 6,144
slots, including two common initial programs per trajectory.

See [protocol](../../docs/IBEX_DEPTH_V1_PROTOCOL.md) and
[code quality audit](../../docs/CODE_QUALITY_AUDIT.md). The producer and manifest
were committed at `06a85b8c` before calls. All 48 cells at 16 slots (768 slots)
are archived as deterministic gzip objects with a hash index and independent
audit. The 64- and 128-slot panels are still running, not complete.
Heavy simulator traces remain scratch, not Git objects.

See [interim findings](../../docs/IBEX_DEPTH_V1_RESULTS.md) and
[`aggregate.json`](aggregate.json). The 16-slot comparison is a predeclared
secondary development breakdown; the primary endpoint remains AUC at 128 slots.

[`execution_status.json`](execution_status.json) is a timestamped progress
snapshot, not a comparative aggregate. Live local status is available with:

```bash
python -m analysis.status_ibex_depth_v1 --root out/ibex-depth-v1
```

Archive and verify each complete panel-wide prefix with:

```bash
python -m analysis.ibex_depth_v1 --root out/ibex-depth-v1 --archive results/ibex_depth_v1
```

The archive reports `complete_study: false` until the full 128-slot panel exists.
