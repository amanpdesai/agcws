# Richer temporal agents — next controlled development step

User direction, 2026-09-07: explore deeper RTL understanding, corrective feedback
and more effective temporal exploration. This extends the research plan without
mixing those changes into the work-allocation diagnostic already underway.

## Separate the questions

1. **Representation:** can proposals satisfy the common work/window contract?
   Finish the v2 allocation diagnostic first, with the existing model/depth.
2. **Information:** does a source-grounded specification and targeted RTL access
   improve decisions over the same agent with schema/summary only?
3. **Correction/exploration:** does richer measured feedback and a behavioral
   archive improve target coverage at the same proposal budget?

A larger prompt, a file-read receipt or more complicated code is not evidence of
understanding. Require short testable predictions about affected windows and the
mechanism/source supporting them; retain whether the next measurement agrees.
This is an observable hypothesis, not a request for hidden chain-of-thought.

## Source-grounded context

The initial [Ibex spec](../specs/ibex.md) separates configuration facts from
activity hypotheses. Count this human-authored specification as per-design
engineering; do not claim that the agent independently discovered every fact.

A future context arm should have a hashed, read-only source bundle: configuration,
mult/div, decoder, execute/control and LSU modules plus necessary definitions.
Require the configuration and relevant mechanism excerpts before its first
proposal. Log file hashes and line ranges retrieved. Cap retrieval/token cost
consistently. A tool can enforce retrieval, not prove comprehension.

**Do not give it the repository root.** This repo contains achieved target
witnesses and reference answers under `results/` and `out/`. Read-only access
would still leak the answers. Whitelist a separate bundle that excludes those
directories, credentials, prior hidden solutions and evaluator internals that
could be exploited. Candidate code executes separately from source-reading tools.

Scaffolding now exists, but is **not connected to the frozen v2 agent**:
`scripts/build_ibex_context.py --out out/ibex-source-context-v1` copies eleven
explicit spec/RTL/configuration files, preserving source headers. The bounded
`SourceReader` verifies a caller-pinned manifest hash, checks file hashes on every
read, and records inclusive line ranges and character usage. Its default 40,000
character allowance is a development setting, not a frozen token budget.
An ablation must pin that budget and the bundle digest before calls.

The reader rejects unlisted paths and symlink escapes. Read-only file modes are
not an execution sandbox: expose only the reader API, never a repository shell.
Mandatory mechanism reads and prediction checks still need controller wiring;
retrieval scaffolding is not evidence that an agent used RTL effectively.

## Corrective feedback to implement and test

- Allocated operation counts per segment, including partial iterations.
- Per-window achieved activity, signed target residual and change from the
  candidate's parent; distinguish failed execution from unmet target shape.
- Retired instruction classes per window from the existing retirement trace,
  aligned to the exact activity window. Separate CSR polling, branches, memory,
  multiply and divide. Label retirement gaps as gaps, not attributed stall causes.
- Precise schema paths and completion violations. A corrected submission uses
  another proposal slot; no free candidate validation/repair side channel.
- Retain successful and unsuccessful mechanisms in a bounded archive instead
  of repeatedly presenting only the latest failure.

Make the same observations and helper functions available to all policies.
Freeze any feedback expansion before its comparison; do not mix panels measured
with different oracles or accounting rules.

## What “interesting” means

Measure coverage/error over independent feasible temporal targets, plus declared
behavioral descriptors such as instruction-class mix and distribution over time.
Novel source text or longer programs alone do not count. Keep useful work and
observation duration fixed. Reserve some proposal slots for different mechanisms
and some for refining an observed near miss; record this allocation in advance.

Compare against strong random sampling and an actual coverage-guided mutation
policy using the same descriptors. An archive-based evolutionary/AlphaEvolve-style
controller is a candidate arm, not a label for the current mutation baseline.

Use observed development targets for controller design. Only after selection,
freeze the controller and introduce fresh target families and held-out seeds.
The goal is to discover whether these mechanisms help; beating random remains
an empirical outcome, not something deeper reading guarantees.
