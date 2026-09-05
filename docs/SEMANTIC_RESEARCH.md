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
coverage; instrumented AES coverage is now running as a measured baseline,
whereas DMA has no coverage arm. Structured goals and gate-level
validation remain necessary for the project's broader claims.

## DMA transaction controls and matched control (2026-09-05)

The legacy DMA driver serialized descriptors despite exposing `outstanding`.
Its partial baseline suite was stopped; those cells cannot establish a
concurrency-sensitive result. The explicit `pipelined` backend now issues
bounded groups of disjoint transfers, checks every transferred byte and
completion tag, and measures outstanding transactions from DUT handshakes.
Seven integration cases passed, including independent read/write backpressure
and an exact deterministic repeat. Requested depths 1/2/4/8 produced peak
in-flight counts 1/2/4/7 under write backpressure. Verification is archived in
`results/dma_pipelining_verification.json`.

A fresh 20-workload calibration spans 4.5476–27.7058 transitions per edge;
all workloads pass the 4096-byte useful-work floor. DMA inherits AES's frozen
epsilon 0.02 without retuning. The new baseline development matrix uses all
five scalar targets and seeds 100–102; old-backend results are not pooled.

`scalar-edit-evolution` is an additional non-LLM control: the same random
initialization, top-four valid parent pool and up-to-eight scalar edits as
semantic-edits-v4, with schema-bounded random edits instead of model advice.
It isolates mutation-interface effects from semantic guidance. Invalid
children consume slots normally. It is running separately on AES and alongside
the new DMA baselines. No held-out evaluation has started yet.

New runs capture source-file hashes, package versions, schema/prompt hashes,
sampling parameters, calibration bounds and pricing configuration before
proposal generation. Missing provider usage after transport failures is
flagged explicitly rather than presented as a known zero-dollar call.

## Catalog-interface candidate (not evaluated yet)

An audit of the first eight completed transaction-backend v4 development
cells found 69 malformed patches in 400 slots: 48 nonexistent object keys,
13 invalid parent indices, four invalid array indices and four attempted
container replacements. These are charged failures, not repaired proposals.
All 96 recorded generation finish reasons were STOP, not token truncation.

`semantic-catalog-v5` is a separate candidate using explicit schema-derived
field IDs rather than invented paths. It retains the top-four parent pool,
scalar-only representation, one-to-eight edits, sampling configuration and
proposal accounting. Its catalog uses the same field enumeration as the
matched non-LLM control. No evidence of improved performance exists yet;
v4 runs continue unchanged and no held-out seed has been used to develop v5.
Use `--prompt prompts/semantic_catalog_v5.txt` with this version.
