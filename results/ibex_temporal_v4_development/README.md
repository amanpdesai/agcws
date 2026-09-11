# Grounded temporal development — complete

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

The 48-cell panel was frozen at `61c1af43` before model calls. Four observed
development targets × seeds 600–602 × random, coverage, base agent and grounded
agent; 16 requested slots per run (768 total). Both agent arms use the revised
response contract and record per-candidate predictions before simulation.
Grounding adds measured execution diagnostics and the persistent experiment
notebook. All policies retain the same language, evaluator and proposal accounting.

All 48 cells and 768 slots are retained, with 421 unique evaluated programs.
Random has the lowest mean AUC (4.831839), followed by base agent (4.990451),
coverage (5.123888), and grounded agent (5.234116). All arms solve 3/12 cells,
only on the near-flat target. No temporal improvement or held-out claim is made.

See [the report](../../RESULTS.md), `aggregate.json`, and
`finalists.svg` (all targets, policies and seeds). The compact evidence includes
raw responses, exact prompts, every trial, functional outputs, phase/operand
diagnostics, frozen source copies, and readiness prerequisites. Large waveforms
and retirement traces remain scratch. Fresh held-out targets/seeds are untouched.

Run `python -m analysis.ibex_temporal_v4 --archive
results/ibex_temporal_v4_development` from the repository root with dependencies
installed. The audit checks artifact hashes, reconstructed payloads/programs,
static failures, score/censor/cost arithmetic, prediction outcomes and unchanged
v3 random controls. It is not an independent simulator/trace rerun.
