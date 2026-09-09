# Ibex v4 — grounded experiment development

Status: implementation; no v4 model calls or comparative results yet.
Completed v1/v2/v3 sources and archives remain frozen. This is development on
observed targets, not a route to retune existing held-out findings.

Initial diagnostic check: parsing the retained v3 `target_0/seed-600/agent-context`
slot 7 execution trace finds 4,096 divides, zero zero-divisor events and 4,096
zero-numerator events. This confirms the mismatch with its stated division-by-zero
hypothesis from executed operand records, not merely reading its source program.
It is an analysis of existing evidence, not a new comparative run.

## Stage A: response-contract gate

Use the first six trials of v3 agent-correction for each of the four targets and
seeds 600–602 as 12 fixed historical contexts. Select by index, never by success.
Reconstruct the same v3 correction payload for both arms. Compare the original
JSON-only response against an explicit bare-program output contract plus native
JSON-schema generation. This isolates a response-contract package, not instruction
wording versus constrained decoding individually. One batch of two per arm/context:
24 calls, 48 requested candidates, no retries or hidden repairs. Counterbalance
arm order by context index. Same Flash model and sampling settings as v3.

Primary: candidate static-schema pass rate over requested slots. Report complete
response adherence separately. Malformed, missing and excess outputs are recorded;
missing slots remain charged. Preserve valid candidates in short batches without
refunding the missing slots. Do not unwrap a nested program. Prediction metadata
errors are separate from workload validity, never mislabeled as hardware failure.
Gate: at least 90% valid candidates in the new arm, with no unsupported API schema
or unknown usage. This small gate assesses interface readiness, not search quality.
Archive raw outputs, payload hashes, exact schema, API metadata and cost. Freeze
code and manifest before calls. An unsupported API is a recorded readiness failure,
not permission to silently substitute another treatment.

The installed google-genai supports `response_json_schema`; server acceptance
must still be tested. Google documents JSON Schema and JSON MIME requirements in
[GenerationConfig](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerationConfig).
The full local validator remains authoritative even when decoding is constrained.

## Stage B: grounded temporal search

After Stage A passes, freeze a separate manifest for random, behavior-coverage,
fixed-contract base agent and fixed-contract grounded agent: four observed targets
× seeds 600–602 × four arms, 16 slots each, two shared initialization slots.
Retain the v3 language, compiler instruction stream, activity window, normalization,
tolerance and simulator binary. Never use fresh held-out seeds for debugging.

Add diagnostics shared by all policies: actual segment/polling phases, operand
events and branch outcomes. Derive phase timing from the executed trace and mapped
assembly, not from release requests. Distinguish measured trace events from
reference-interpreter predictions. Preserve the exact instruction stream; labels
or disassembly analysis must pass binary/measurement equivalence gates. Do not
call retirement gaps stall causes without corresponding hardware evidence.

The grounded arm additionally presents a bounded experimental notebook: reference,
declared change, per-window direction prediction, actual program diff, and observed
outcome. Store predictions before evaluating candidates. Match deltas only to a
valid prior reference; a mismatched or absent reference is an unscorable prediction,
not an invalid workload. One refinement and one exploration per batch remain
instructions, not claims of compliance. Measure actual edit scope.

Primary: proposal-indexed best-so-far temporal AUC. Secondary: solve/target coverage,
per-run behavior coverage, validity, prediction availability/direction accuracy,
edit scope, tokens and estimated dollars. Report prediction metrics on their
explicit scorable denominator with missingness; never drop failures from primary
AUC. The direction neutral band is 0.01 in frozen envelope-normalized units,
inclusive at both boundaries; outside it, classify the signed change as increase
or decrease. Retain the last six non-initialization experiment records, including
invalid candidates and contradicted predictions. These settings must be in the
Stage B freeze before calls.
Compare the grounded package as a whole; do not claim its components are isolated.

## Completion criteria

Unit tests, real-CPU diagnostic equivalence, fixed manifests, complete bounded
panels, independently recomputed compact archives, trajectory diagnosis, plots,
honest recommendation and verified push. Improvement is empirical, not a gate
that permits indefinite tuning. Any revision after observing a stage is a new
version. Fresh held-out targets/seeds remain reserved for subsequent confirmation.
