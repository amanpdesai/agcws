# Temporal surrogate screening qualification

Completed 2026-09-10 under the [frozen CPU protocol](../../docs/SAGA_TEMPORAL_V1.md).
This is **temporal-ridge-screen-v1**, a SAGA-inspired adaptation using GeST
operators. It is not execution of SAGA's original full optimizer or a paper
reproduction.

## Observed outcome

| Counter | Value |
|---|---:|
| Generated and charged proposals | 12 |
| Selected evaluations / actual simulations | 8 / 8 |
| Valid measured workloads | 8 |
| Filtered, unknown-validity proposals | 4 |
| Cache hits | 0 |
| Best measured normalized target error | 0.15699402710315408 |
| Model calls | 0 |

All four bootstrap programs passed. Both subsequent four-candidate batches
used previously measured data to select two candidates before any batch outcome
was visible. Filtered proposals have null validity, rates and measured loss;
they are not schema failures, failed workloads, or scored successes. No proposal
reached the frozen 0.1 tolerance. No replacements were drawn.

Eight simulations instead of twelve is an accounting fact, not demonstrated
savings at equal quality. Filtered outcomes are unknown. There is no matched
control arm, and the previous GeST smoke used a different seed and budget;
its best error must not be compared as evidence for or against screening.

## Upstream predictor diagnostic

`upstream_probe.json` records the actual pinned SAGA predictor in an isolated
NumPy 2.4.2 / SciPy 1.17.1 environment. A known positive logarithmic input
produced the exact expected extrapolation, 15.9903172823362. Negative fitness
produced log/covariance warnings and zero output. This confirms the need to
change the fitness/predictor contract for temporal loss rather than silently
feeding it GeST's negative-error fitness.

The new temporal ridge predictor does not reuse that extrapolation routine.
It uses fixed positional phase features and eight-output ridge regression;
changes, limitations and selection rules are enumerated in the protocol.

## Evidence and verification

`manifest.json` records committed producer/source hashes, NumPy version,
target and runtime identities. `decisions.json` contains every generated
candidate, training slot list, predicted profile/error, feature-space distance
and pre-measurement selection. `trials.json` contains all twelve accounted slots.
`evaluations/` stores compressed real CPU records, assembly, logs and profiles;
no waveforms are committed.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m experiments.saga_temporal_v1.qualification audit
```

The audit reconstructs proposals, selection and training visibility; independently
checks CPU/reference state, generated assembly, activity/window arithmetic and
measured losses; and verifies the summary. It does not independently resimulate
the waveforms. Initialize pinned submodules before auditing.

All 569 repository tests pass with three pre-existing Ray/fork warnings; active
code passes Ruff. Earlier GeST and temporal-scaling archive audits still pass.

Next: a balanced development target bank, matched no-screening control, and
separate measured-versus-proposal-budget views. Evaluate filtered outcomes only
in a separately charged diagnostic tier withheld from search. Fresh-seed Pro
confirmation remains unchanged and has not been launched by this milestone.
