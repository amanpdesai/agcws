# Ibex temporal context/correction ablation — development protocol

Status: implementation and gates; **not frozen and no comparative calls yet**.
This extends the completed v2 diagnostic without changing its source or results.

## Question and arms

Does source-grounded context or a corrective-feedback/exploration package improve
temporal targeting once exact-work arithmetic is handled by the common language?

| Arm | Source excerpts | Enhanced feedback and exploration archive |
|---|---|---|
| agent-base | No | No |
| agent-context | Yes | No |
| agent-correction | No | Yes |
| agent-combined | Yes | Yes |

Also run random sampling and behavior-coverage-guided mutation. This is a 2×2
development ablation of the agent packages, not isolation of each individual
feedback field or proof that reading causes understanding. The coverage baseline
uses measured retirement-gap bins and dominant instruction class; it is not RTL
code coverage. Its structural operators insert/delete operations or segments,
reorder segments, and change values. Restarts are explicitly counted.

## Common contract

- Reuse four **observed development** target profiles and seeds 600–602 from v2.
  No new held-out targets or seeds are exposed. Six arms × four targets × three
  seeds = 72 cells, each with 16 slots and two shared initialization slots.
- Batch size two; seven model feedback rounds after initialization. Same Flash
  model, temperature 0.7, top_p 0.95, thinking budget 512 and output limit 8192.
- Exactly 4,096 semantic operations and the unchanged 200,000-cycle eight-bin
  activity interval. Same target scale and tolerance as v2; no difficulty tuning.
- Integral numeric encodings are canonicalized for **every** policy. `1.0` and
  `1` denote the same schema integer. Fractional, out-of-range, boolean and
  nonfinite values are rejected, not repaired. Preserve submitted and canonical
  forms in the ledger; canonicalization is not a free search attempt.
- Every requested slot counts, including missing/invalid/duplicate candidates.
  No free repair calls. Cache access is common; all cache hits still consume slots.
- Preserve random's v2 sampler as the reproducible control. Coverage mutation is
  a new structural policy, not a claim to reproduce v2 mutation. All policies
  have the same legal language and observations available to their controller.

## Information and correction

Source arms receive fixed, bounded excerpts from a hashed allowlisted bundle,
including configuration and mechanism RTL, with line/hash receipts. No repository
shell, target witnesses, credentials or solution files. This is supplied source
context, not autonomous RTL discovery. Request a brief testable window prediction
with source references; retain responses without treating citations as proof of
comprehension. Count the human-written specification as per-design engineering.

Enhanced feedback adds exact schema paths, allocation, completion time/margin,
per-window retirement classes and gaps, and changes relative to a declared
reference candidate. Gaps are not attributed to specific stall mechanisms.
The controller presents a bounded archive of distinct measured behaviors and
requests both refinement and exploration within the same two-slot batch.
This entire package is the correction treatment; its components are not isolated.

## Endpoints and freeze

Primary descriptive endpoint: mean best-so-far normalized-error AUC over all
declared cells, retaining invalid slots and the v2 error cap/curve convention.
Secondary: final error, solve counts, right-censored proposals-to-target, validity
by stage, matched per-run behavior-bin coverage, input/output/thinking tokens and
estimated cost. Do not compare global unions with unequal target-conditioned
sample counts as if they proved expressiveness. Missing cells block completion.

Before calls, freeze the protocol, prompts, source bundle/excerpts, controller,
descriptor thresholds, cache provenance and model settings in a committed manifest.
Archive every result. No mid-panel tuning. Any selected controller still requires
a new freeze and fresh target families/seeds before confirmatory claims.

Readiness gates: numeric real-CPU equivalence; feedback/activity interval equality;
unit checks for archive selection and budget accounting; model payload isolation.
The gate outcome does not substitute for completing and analyzing the 72 cells.
