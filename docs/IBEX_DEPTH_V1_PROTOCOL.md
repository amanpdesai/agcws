# Ibex closed-loop model × depth development protocol

2026-09-08. Freeze this file, producer sources and manifest before any model call.
This is new development, motivated by the completed capability probe. It is not
held-out confirmation and does not amend earlier frozen studies.

## Question and panel

Does stronger next-batch proposal quality compound into better on-policy temporal
search? Compare Pro-4096, Flash-4096, uniform random and behavior-coverage search.
The last is an executed-behavior archive, not RTL branch-coverage fuzzing.
Flash-4096 controls thinking allowance when comparing model families.

Use the four existing v4 achieved temporal targets and new development seeds
610–612. All four targets remain, including near-flat target 1. Each policy
builds its own history. Two seed-determined random initial programs are shared
across policies and count against budget; subsequent batches contain two proposals.
No filtering or resampling of invalid initial programs. No warm-start from v4
histories, reference solutions, capability candidates or held-out records.

Run 48 trajectories to 128 slots each (6,144 slots); derive 16/64/128 prefixes
from the same trajectories. Execute panel-wide prefix stages in that order.
Continue after tolerance so depth comparisons have complete curves. At most
1,512 model calls: 24 agent trajectories × 63 calls. No optional stopping on
method ranking, no extra seeds chosen after looking at results.

## Fixed controls

Unchanged v4 grounded payload: typed complete programs, fixed semantics, best
four/recent four historical trials, executed phase/operand diagnostics and last
six prediction/outcome notebook entries. Same native response grammar, strict
local validator, and prediction contract. Missing predictions do not invalidate
otherwise legal programs and are reported separately. Short batches retain valid
slots and charge the missing slots; excess batches are rejected, never truncated.
References must have been valid before the batch; same-batch feedback is forbidden.

Unchanged CPU image, binary, RTL, allocator, compiler, fixed measurement window,
4,096 semantic operations, 200,000 cycles, eight bins, scale 528.45376 and
tolerance 0.1, all verified against the parent manifest. No GLS claim is added.

Models are exactly `gemini-2.5-pro` and `gemini-2.5-flash`, global Vertex endpoint,
thinking allowance 4,096, temperature 0.7, top-p 0.95, output cap 16,384. Actual
model version and thinking usage are recorded. No API generation seed is sent;
the experiment seed controls initial programs and CPU search, not cloud determinism.
No model substitution, JSON repair, fallback proposer or SDK retry is allowed.

## Endpoints and analysis

Primary: mean AUC of best-so-far normalized target error at 128 proposals,
trapezoidal integration over indices 1..128. Lower is better. Publish 16/64
prefix AUCs as declared depth breakdowns and AUC/(N−1) for readable cross-depth
comparison. Before any valid proposal, the curve uses explicit sentinel 1.0;
the first valid loss replaces it even if above 1.0. This sentinel is not a score
or a ceiling; invalid workloads never acquire a power/activity score.

Secondary: final error, solve count, right-censored evaluations-to-target (N for
unsolved), failure stage, unique programs, prediction-direction accuracy, tokens,
estimated dollars and runtime. Always pair solve counts with censored timing.
Report equal-valid-evaluation curves as descriptive secondary analysis, including
how many valid evaluations each comparison retains; never replace the primary.
Describe paired differences averaged across four targets within each seed.
With three seed units, do not make significance or equivalence claims. Publish
all target/seed cells, not just non-flat successes or favorable budgets.

## Failure, cost and execution policy

Missing usage fields are unknown, not zero-cost. Every model request has a durable
request-start marker and saved response before simulation. API failures consume
both requested slots with explicit API status and unknown-cost reservation; no
automatic retry. Unexpected local/infrastructure errors halt the affected stage,
preserve evidence and cannot be converted into workload invalidity. An interrupted
request without a saved response requires explicit resolution; resume never
silently issues it again. Completed batches are immutable and replay-checked.

Use up to four supervised trajectory workers and serialize model calls. No
detached shell workers, process alarms or simulation wall-clock cutoff. The SDK's
120-second transport deadline is explicit, not a workload timeout; a transport
failure is recorded as API failure rather than schema failure. A study-wide lock
prevents simultaneous runner processes. CPU containers use the existing read-only
checkout, dedicated output mount and `--rm` wrapper.

Fresh prices checked against [Google's standard Vertex pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing):
Flash input/output $0.30/$2.50 per million; Pro $1.25/$10 at ≤200k input,
$2.50/$15 above. Thinking is included in output. This is not billing reconciliation.
Enforce a $180 study ceiling using known cost plus conservative reservations for
unknown/in-flight calls. Input text/schema bytes plus 4,096 must not exceed
200,000 (conservative payload bound); reserve the short-context maximum output
per call. Refuse oversize requests explicitly—do not silently truncate context.
If the ceiling or endpoint identity check prevents continuation, archive the
incomplete panel and request direction; do not resize or replace the study.

## Evidence and scope

Track protocol, manifest, source snapshots, targets, all per-batch payloads/raw
responses/trials, compact CPU checks, complete prefix summaries, aggregates and
hashes in `results/ibex_depth_v1/`. Heavy waveforms remain scratch; no deletion
or lossy replacement of evidence is part of this run. Verify compact evidence
from a clean export before calling the panel complete.

Select no new architecture or source-reading tool during this study. A positive
development ordering supports a fresh held-out protocol, not a general claim
that agents outperform fuzzing or possess a more expressive language.
