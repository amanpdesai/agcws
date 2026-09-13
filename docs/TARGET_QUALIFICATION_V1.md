# Five-design target qualification v1

Frozen procedure before new calibration or witness-search measurements.
This is CPU-only readiness work, not the paid comparison. Historical targets,
studies and their normalization are unchanged.

## Independent calibration

Each backend samples its existing `random` generator for 32 proposals on each of
seeds 7200 and 7201. Two-slot batches, no early stopping, no model calls, identical
zero-vector placeholder target that the generator does not inspect. This target
is not a research request and its solve rate is irrelevant. Both seeds run
concurrently; designs may run concurrently as well.

Retain every proposal and every invalid result. Require at least 32 valid
observations, otherwise stop that design's qualification and report the failure.
Use the 5th and 95th percentiles of all valid per-bin rates, with Python's inclusive
quantile definition, as low/high calibration endpoints. Their difference is the
fixed error scale. Also record extrema, the range of whole-window means, and
the median whole-window mean. Degenerate endpoints or a median outside them stop
qualification. These are activity units, never watts.

## Requested bank

Eight analytic families plus a separate flat control, as enumerated in
`pipeline/targets.py`. Development and confirmation amplitudes are different.
For Ibex, mesh and RedMulE use `requests(low, high, split=...)` unchanged.
For AES and DMA use `mean_matched_requests`: center each analytic shape on its
own arithmetic mean, scale it to stay inside calibrated endpoints, multiply
amplitude by 0.75 (development) or 0.90 (confirmation), then add the calibrated
median whole-window mean. Flat controls equal that mean. Their duplication
across splits is explicit; they are controls, not held-out non-flat evidence.

Reason: AES/DMA enforce exact work and idle budgets. Giving different families
different total target activity would confound shape with a possibly unreachable
mean. Mean matching preserves shape and the resource contract, not feasibility.
It may yield insufficient non-flat amplitude, which is a qualification failure,
not permission to loosen the criterion.

## Witness search and admission

Freeze all requested vectors before search. For each design, split and family,
run phase-random and phase-GA for 256 proposals each, using seed 7300 for
development and 7400 for confirmation. Two-slot batches, no early stopping.
Record all attempts and costs, including invalid proposals and missed requests.
Select the valid witness with lowest normalized RMS error; ties use policy name
then proposal index. Witnesses and calibration programs are not agent context.

A witness must pass functional/useful-work checks and reach error <=0.10. A
non-flat target must have constant-vector floor >0.12. Flat-control target and
witness floors must both be <=0.10. Record pairwise distances between requests,
first-hit proposal counts by baseline, validity and failures. Close or duplicated
targets do not establish diversity merely by having different names.

No failed target is replaced by an achieved profile. No extra search budget,
amplitude adjustment, or target substitution is allowed within this version.
If this procedure fails to yield eight substantive targets on a design, retain
the complete result, diagnose the contract or search limitation, and explicitly
version any proposed remedy before another qualification run. The five-design
readiness goal remains unmet until the requested bank is genuinely demonstrated.

Qualification budgets are not paper budgets. Full-study execution, fresh policy
seeds, Flash/Pro comparison and paid-panel launch remain separately gated.
