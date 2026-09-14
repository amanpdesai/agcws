# Five-design bounded feedback smoke v4

Declared before paid v4 calls. New bounded history and exact-budget context
require new smokes; v2/v3 failures remain unchanged. All banks now use the
current runtime. RedMulE uses its separately qualified long-window bank.

For each of five designs, use every development and confirmation request:
18 targets, seed 8502, Flash-4096/phase-random/phase-GA, 16 proposal slots,
batch size two, two shared initialization slots, no early stopping. Maximum
126 model calls and $12 accounted ceiling per design ($60 total ceiling).
This is not the full study or paper inference. The seed is fixed before calls;
no favorable-seed retries or fallback model are permitted.

Run at most one provider call per design, five in total, with 18 cell workers
per design. This bounds concurrency separately from CPU throughput. The
existing provider retry/error accounting remains unchanged. Any API failure
and unknown liability must remain visible and fail the existing strict smoke
readiness check; do not weaken that rule in response to results.

Each target must have a valid model-generated measured workload whose feedback
appears in a subsequent call. Initialization alone does not pass. Audit all
payloads, parsed output, cache profiles, proposal slots, token/model/schema
provenance and known/unknown cost. Strict readiness requires every target to
pass, with all calls having known usage, no API error and the expected model.

Only target vectors and the shared calibration scale enter study settings;
qualified witness programs, constructor cases, calibration search strategies
and witness-selection diagnostics never enter model payloads. Both target
splits are exposed during engineering smokes: future fresh-seed results must
not be described as unseen-target generalization.
