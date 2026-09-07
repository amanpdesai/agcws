# Ibex temporal expressiveness development v1

This is a new exploratory pilot, not a replacement for either frozen AES/DMA
study. The protocol and manifest were committed at `e5d753c` before any
comparative run. The manifest defines 36 cells and 576 requested proposal slots.

Current state: feasibility gate passed; comparative execution is in progress.
Do not treat the manifest alone as completed results. Completion requires all
36 per-cell summaries, ledgers, `aggregate.json` and the archive hash index.

Execution note (2026-09-07): after verifying 96 logical CPUs and a load near 27,
six later cells (`target_3`, agent/mutation, seeds 600–602) were started through
separate supervised foreground sessions alongside the original three-worker
queue. As those workers finished, the six `target_2` agent/mutation cells used
the freed capacity. Maximum concurrency is nine. No controller, target, budget, source or
model setting changed. The original queue skips these directories rather than
duplicating them; completion is determined from audited artifacts after both
sets of sessions finish, not from a queue status alone. Wall-clock figures
include variable concurrency and shared-cache waiting and are not equal-resource
policy speed comparisons.

## Reproduce

Use the image ID and pinned Ibex revision in `manifest.json`. The managed
container mounts the checkout read-only and writes only to the artifact root.
This new experiment's source is in the checkout, not baked into that older
image. It is not an image-only portability claim.

```bash
export AGCWS_CONTAINER_IMAGE=agcws:window-validation-v1
export AGCWS_CONTAINER_OUTPUT="$PWD/out/ibex-expressiveness-v1"
bash docker/run.sh fusesoc --cores-root=/workspace/third_party/ibex run --target=sim --setup --build --build-root=/workspace/out/toolchain lowrisc:ibex:ibex_simple_system --MHPMCounterNum=12
.venv/bin/python -m experiments.ibex_temporal_v1.gate --root out/ibex-expressiveness-v1
.venv/bin/python -m experiments.ibex_temporal_v1.panel run --root out/ibex-expressiveness-v1 --manifest results/ibex_temporal_development_v1/manifest.json --workers 3
.venv/bin/python -m analysis.ibex_expressiveness --root out/ibex-expressiveness-v1 --archive results/ibex_temporal_development_v1
.venv/bin/python -m analysis.ibex_expressiveness --archive results/ibex_temporal_development_v1 --verify
```

The gate expects a fresh output directory. The panel skips completed cells but
refuses to overwrite incomplete ones. Inspect failures explicitly; do not erase
failed runs or silently substitute a changed controller. Source hashes are
checked at the beginning of every cell. Model credentials remain on the host;
they are not mounted into simulator containers. Vertex needs the existing ADC
and project configuration in the ignored `.env`.

The run seed fixes local generators and shared initialization. Vertex sampling
is stochastic; no provider-side deterministic seed is claimed. Exact model
response identifiers and raw generation diagnostics are retained per batch.
Reported costs use [Google's published Vertex pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)
and recorded usage, not a billing export. Uncertain usage is flagged separately.

## Interpretation

Primary: target-error AUC at sixteen proposed slots. Secondary: target solves,
right-censored time-to-target, validity stages and descriptive profile diversity.
There is no superiority test on this three-seed development panel. Feasible
witnesses are independent of the random sampler but selected by the researchers;
they are not an unbiased sample of all CPU behaviors.

This measures effective coverage inside one shared bounded program language.
It does not establish a larger language for the agent, unrestricted program
discovery, cache behavior, or power accuracy. The fixed-work constraint counts
semantic body operations, not equal retired instructions or equal energy.
Busy-wait instructions contribute real activity; no idle-power assumption is
made. Changing hardware, controller and target construction together cannot
isolate a causal contribution from semantics.
