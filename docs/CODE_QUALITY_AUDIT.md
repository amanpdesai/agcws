# Active research-path quality audit

2026-09-08. Scope: the new Ibex closed-loop runner and the evaluator, response
contract, history renderer and behavior archive it calls. This is not a claim
that every historical script has been rewritten or that tests prove no bugs.

## Clean boundary for new runs

`experiments/ibex_depth_v1/` separates immutable storage, metered model transport,
metric definitions and orchestration. Unknown policy/model names fail explicitly.
There is no catch-all dispatch to coverage, repair prompt, replacement model or
random proposer when the agent fails. Missing token metadata is unknown cost,
not a successful zero-dollar call. API exceptions are recorded and charged as
API failures; unexpected infrastructure exceptions propagate and halt new work.

Atomic immutable batch records preserve proposals before simulation. Resume
reconstructs deterministic CPU state and checks identities/payloads before using
saved responses. An unresolved request marker prevents paid resampling. A
process lock excludes competing runners; an API lock serializes calls and the
cost ceiling. Local evaluator failures are not silently converted into scores.
The fixed useful-work observation window remains part of the task, not a shell
timeout. The SDK transport deadline is separately declared in the protocol.

The primary curve has an explicit pre-valid sentinel; the first valid value is
not clipped to that sentinel. Failure stages, prediction missingness and unknown
usage remain distinct. Short outputs retain valid proposals while charging all
requested slots. JSON numeric canonicalization follows the existing declared
schema semantics; it does not invent or unwrap malformed workload structure.

## Historical code is not automatically dead code

The previous runner contains permissive legacy adapters and retry paths. New
generation does not invoke those paths. They are retained because older studies
pin their exact sources and hashes. Removing or editing them in place would
break clean-checkout verification of published evidence. Likewise the v4
unannotated evaluator option is used by CPU equivalence tests, not dead code.

The active graph still reuses the proven v4 evaluator, v3 program interpreter
and behavior archive, and v4 context renderer. Its historical imports are
documented dependencies, not an excuse to silently execute old policy logic.
The new runner has no duplicated dormant retry/repair or alternate-output paths.
Demonstrably unused imports in the maintained `src/` package are checked with
Ruff's full F rules; frozen study sources are not mechanically rewritten.

## Verification and remaining risks

Tests cover immutable writes, invalid dispatch, missing usage, price tiers,
no-score invalidity, censoring, un-clipped loss, response-before-simulation,
short-batch accounting and resume without a second API call. The full existing
suite remains required before freezing. Archive analysis must independently
reconstruct payloads, proposals, primary metrics and compact CPU checks.

Remaining limitations are explicit: the legacy cache diagnoses two known DUT
failure modes from evaluator logs; an unknown log failure raises instead of
guessing. Runtime/package/source fingerprints must match. Unexpected interruptions
inside a cache evaluation require inspection, not a fallback simulator. Stored
compact evidence is not an independent replay of every waveform. The existing
Ray/fork warnings are not silently suppressed.

Verification checkpoint: 513 tests passed, with the three existing Ray/fork
warnings; lint passes for `src/`, the new runner and its analysis/tests. The
previous capability archive (72 cells / 144 slots) and v4 archive (48 cells /
768 slots) independently pass their compact-evidence audits unchanged. This
does not imply completion of the new depth panel.
