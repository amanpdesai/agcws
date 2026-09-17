# ibex — frozen three-arm baseline evidence

270 completed cells: nine profiles × ten seeds × phase-random, phase-GA and
phase-model. 128-slot cap; batch-two stopping at max normalized bin error ≤0.05.
No LLM calls. Source/runtime manifests are in the packed evidence and the
[original plan](../baselines-model-v1-plan/).

The single [results report](../../../RESULTS.md#completed-five-design-baseline-matrix--2026-09-17)
and [matrix index](../../baselines_model_v1/README.md) provide aggregates,
limitations and reproduction instructions. Shards contain compact raw evidence;
waveforms and compiled tools are not included. Preserve every shard and
`evidence.pack.json.gz` together.

```sh
.venv/bin/python maintenance/archive_study.py restore --source results/ibex/baselines-model-v1 --destination /tmp/agcws-ibex-review
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m analysis.publish_baseline_matrix --design ibex --root /tmp/agcws-ibex-review --output /tmp/agcws-ibex-audit.json
```
