# Measured-feedback witness refinement v4

Frozen CPU qualification extension for mesh and RedMulE. Preserve every earlier
version. Targets, scales, observation windows, useful-work/functional gates and
admission criteria remain unchanged. This is not matched-budget policy evidence.

For each request, choose the lowest measured-error valid parent from completed
v1 panels (mesh and RedMulE) and v2/v3 pulse searches (RedMulE only). Ties use
source path/slot. Record source manifests and selected parents before new
measurements. Replay each parent exactly; a rate mismatch stops the run.

Maximum 257 proposals per request: one initial replay and 128 paired edit batches.
Each pair changes one phase start, duration or job/packet count negatively and
positively from the same incumbent. Skip duration for one-job phases. Coordinates
are shuffled deterministically each sweep with seed 8000 development / 8100
confirmation plus sweep index. Timing step sizes by batch index are 256 (0–15),
64 (16–31), 16 (32–63), 4 (64–95), 1 (96–127) cycles. Count edits are always ±1.
Do not clamp illegal edits: validation rejects them and the slots still count.

After both measurements, accept only strictly lower measured error. Stop when
the incumbent passes qualification, at the initial check or after a complete
pair. No structural insertion/deletion or operand-pattern changes in this
version. A miss remains a miss; do not add attempts after inspecting outcomes.
Eighteen requests may run concurrently. Retain every proposal and rejection,
parent visibility and final witness. Immutable checkpoints and shared measurement
cache support replay/resume without new simulator invocations for cached work.

Admission remains error <=0.10 and non-flat target constant-vector floor >0.12;
controls additionally require target and witness floors <=0.10. No surrogate
prediction is consulted. No agent sees the private parent programs. No paid calls.
