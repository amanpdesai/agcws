# Ibex all-bin pilot — cost-interrupted exploratory evidence

Success requires every bin's absolute error divided by the frozen calibration
width to be <=0.05. One alternating target, seeds 9500 and 9501, four arms,
128 slots, shared initializations and batch-two early stopping. RMSE remains
the ranking/AUC objective, not the success gate.

| Arm | Seed | Measured slots | Best maximum-bin error | State |
|---|---:|---:|---:|---|
| Pro | 9500 | 40 | 0.064915 | Cost-interrupted |
| Pro | 9501 | 12 | **0.023667** | **Solved at slot 11; batch charged through 12** |
| Flash | 9500 | 58 | 0.289983 | Cost-interrupted |
| Flash | 9501 | 56 | 0.065422 | Cost-interrupted |
| Phase-GA | 9500 | 128 | 0.683557 | Budget exhausted |
| Phase-GA | 9501 | 128 | 0.762898 | Budget exhausted |
| Phase-random | 9500 | 128 | 0.768430 | Budget exhausted |
| Phase-random | 9501 | 128 | 0.633696 | Budget exhausted |

79 calls; estimated model liability $3.58204965. The configured $3.66 remainder
cap prevented another reservation, stopping the entire panel. Combined with
the two earlier pilots, estimated liability is $9.91681075. No automatic restart.

This demonstrates one Pro workload with all eight bin averages accurate; it
does not demonstrate cycle-wise tracking or statistically establish superiority.
Three model cells are cost-interrupted, not completed 128-slot failures.
Do not compare full-budget mean AUC across this incomplete panel. The target
and seeds were exposed during prior exploratory runs; this is not held-out.

[Summary](summary.json) retains all eight cells, terminal summaries and explicit
interruption states. [Compressed evidence](evidence.json.gz) contains exact-text
checkpoints and SHA256 for manifests, requests/responses, proposals, trials,
cached measurements, completions and failures. Large waveforms remain scratch.

`analysis/publish_maxbin_pilot.py` verifies frozen source/runtime identity,
contiguous slots, proposal/trial equality, cached bin rates, RMSE and all-bin
errors, terminal metrics and metered liability. Compression roundtrip is
checked. This is an arithmetic/checkpoint audit, not independent resimulation
or a full model-feedback trajectory audit. No full matrix was launched.
