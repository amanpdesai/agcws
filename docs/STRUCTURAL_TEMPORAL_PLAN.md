# Structural temporal study — development plan

Started 2026-09-06. This is a new research track, not a revision of the
completed scalar held-out results. No success or model advantage is assumed.

## Interface diagnosis

Replaying every archived v4 invalid patch against the original batch's four
parents reproduces the failures. AES: 473 invalid object keys, 34 invalid
parent indices, 14 invalid array indices, 24 empty/invalid paths, 4 missing
parent fields; 12 additional slots have no candidate. DMA: 210 invalid parent
indices, 197 empty/invalid paths, 15 invalid array indices, 4 invalid object
keys; 20 additional slots have no candidate. The reproducible diagnostic is
`results/semantic_patch_failure_audit.json`.

These failures were already charged in the scalar study. They are not all
malformed JSON or hardware protocol errors. The next interface should expose
complete typed schedules and explicit structural operations instead of making
the model guess mutable nested JSON paths. No free resampling or hidden repair.

## First milestone: AES capability and small comparison

Use a common bounded sequence DSL: `work(units)`, `wait(cycles)`, and
`repeat(count, body)`. Expansion is deterministic and limited in depth and
operation count. Unknown fields, invalid counts, and expansion bombs fail
before simulation. All policies receive the same grammar and contract.

The first AES contract is exactly 64 AES-128 encryption blocks, a fixed data
pattern, and exactly 6000 idle cycles. Reordering and repartitioning work/idle
changes temporal activity without changing useful work. A common adapter
lowers the schedule into the existing reference-checked transaction harness.
Do not present this restricted first milestone as general AES mode synthesis.

`results/structural_temporal_aes_verification.json` verifies compact repeat
and explicit expansion produce identical activity artifacts, and two random
structural schedules produce different eight-bin profiles. All four execute
64 correct blocks over exactly 6774 clock edges, including the same reset
window. This is representation verification, not a search result.

Next implement shared structural operators and random/evolutionary policies,
then agent-only and hybrid proposals with precise contract-error feedback.
Give all methods identical legality mechanisms. Charge every requested slot,
including rejected proposals and missing model responses. Keep candidate
failure details separate from the hardware validity stages.

## Temporal measurement and feasibility

Use eight equal-clock bins over a declared common observation window.
Compare raw bin rates with one fixed, recorded normalization scale derived
from target/calibration data. Do not normalize each candidate by its own peak;
that discards amplitude error. Keep the old temporal loss for historical
reproduction and introduce a separately versioned fixed-scale endpoint.

Construct targets from actual achieved profiles in a separate reference
corpus; archive their reference workloads but do not give those solutions to
search policies. Hold useful work and simulation duration fixed, and reject
window mismatches rather than silently clipping traces or rescaling time.
Tolerance and scale must be set on development data before final evaluation.

## DMA transfer and evaluation gates

Transfer the same schedule/controller interface to descriptor-driven DMA.
Define the work-unit lowering, mapped memory layout and legal concurrency
explicitly. Verify every transfer, useful-work total and measurement duration.
DMA completion latency can depend on schedule/backpressure, so equal requested
idle cycles alone do not establish equal observation windows. A fixed horizon
with explicit completion checks/padding must be verified on both RTL and GLS.

Run small development pilots first. Compare random, structural evolution,
agent-only and hybrid with the same proposal budget and target information.
Select one controller across both designs, not one per design. Before any
confirmatory run, record targets, source/model/prompt, loss, tolerance, budget,
seed range, selection rule and paired inference in a new freeze manifest.
The observed scalar evaluation seeds 200–209 are no longer held out; do not
reuse them for confirmatory conclusions. Capability seeds 300–301 used here
are development-only. Reserve fresh evaluation seeds after the pilot.

Validate representative finalists with direct GLS and matched waveform windows.
Report activity targeting unless gate-level evidence supports power targeting.
Archive all complete panels, invalid proposals, unknown usage and limitations.
No larger matrix or model sweep until the end-to-end pilot is mechanically sound.
