# Semantic workload search: development record

The next research step is semantic mutation of valid parents across AES and
DMA, followed by structured profile targets. Development uses seeds 100–102;
seeds 200–209 remain held out. A single winning cell is not a parity result.

## Audit findings

Legacy Vertex history included entire waveforms and unsigned losses, and its
payload omitted the useful-work floor. Repair attempts were not independently
charged proposal slots. The one-shot and offline-hybrid arms were heuristics,
not real LLM comparisons. Old cost estimates omit thinking tokens.

The prior epsilon refresh used a single corpus rather than the declared
median of five random seeds. Rechecking the completed random matrix's first
20 proposals gives target-solve fractions [0.8, 0.6, 0.6, 1.0, 0.6] at
epsilon 0.05: median 0.6. The declared rule would retain 0.05. At 0.02,
fractions are [0.2, 0.2, 0.4, 0.4, 0.4]: median 0.4. These are retrospective
checks, not a pre-run calibration. Current 0.02 matrices are exploratory
tight-tolerance comparisons. They must not be called the preregistered primary
study; this needs reconciliation before confirmatory evaluation.

## First development probe

AES q=0.50, seed 100, 50 proposals, batch size four, epsilon 0.02. All policies
solved this cell; random and semantic policies started with a successful
random workload. Differences below describe refinement precision, not improved
solve rate. Evolutionary search has a different initialization implementation.

| Policy | AUC (lower better) | Valid proposals |
|---|---:|---:|
| Random | 0.608088 | 50/50 |
| Evolutionary | 0.694242 | 50/50 |
| Semantic full workloads v2 | 0.608088 | 8/50 |
| Semantic scalar edits v3 | 0.394775 | 25/50 |
| Semantic scalar edits v4 | 0.142459 | 42/50 |

V2 and V3 encountered MAX_TOKENS. V4 limits thinking to 512 tokens and allows
8192 output tokens; its cost estimate includes reported thinking tokens.
These versions were iterated on development data. No confirmatory inference
is justified by this probe. V4's scalar edits restrict child representations;
full workload structure still comes from random initialization.

The ongoing five-target development suite automatically archives compact
workloads, validity, measured profiles, goal, model metadata, and summaries
under results/semantic_v4_development_aes as cells finish. A manifest records
the source commit, prompt hash, model, envelope, seeds and budgets. The
summary command refuses incomplete matrices.

## Next comparisons

The legacy AES development suite was stopped after discovering that its
simulator receives only block count, pattern and idle controls: key lengths
and encrypt/decrypt operations in the DSL were ignored, and reset occurred
between blocks. Completed legacy cells remain useful as pacing experiments,
but cannot establish semantic control over encryption modes or key lengths.

The new transaction backend executes ordered operations with one reset per
workload, actual key length and direction, and a cryptography reference check
on every block. Its activity is restricted to the DUT hierarchy and its
coverage metric is instrumented Verilator basic-block line coverage. All 28
integration checks passed (24 key/direction/pattern combinations, idle timing,
two deterministic repeats, and mixed key/direction sequences). A fresh
calibration is required; legacy bounds cannot be reused.

Verification evidence is in results/aes_transactions_verification.json.
The transaction backend is selected explicitly with --backend transactions;
legacy results are not silently changed by the new implementation.

Complete the development suite before selecting a frozen policy. Run DMA
with the identical controller, then held-out evaluation. Add real one-shot
and hybrid agents, and a matched generic scalar-edit operator to isolate the
LLM's contribution. Coverage-guided fuzzing requires actual instrumented
coverage; it is not yet a measured baseline. Structured goals and gate-level
validation remain necessary for the project's broader claims.
