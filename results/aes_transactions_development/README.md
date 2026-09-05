# AES transaction-backend development comparison

Completed 2026-09-05. This directory contains five policies × five scalar
targets × three development seeds = 75 runs, each with 50 proposal slots.
The separately archived matched scalar-edit control adds 15 runs, giving
the six-policy comparison in `comparison.json`. All 4,500 slots passed an
independent audit of measured losses, AUC, censoring and accounting.

| Policy | Mean AUC ↓ | Solved / 15 | Valid proposals |
|---|---:|---:|---:|
| semantic-edits-v4 | 1.6073 | 14 | 82.9% |
| scalar-edit-evolution | 1.7473 | 14 | 76.9% |
| random | 2.1849 | 12 | 100% |
| coverage-guided-line | 2.8559 | 7 | 100% |
| evolutionary | 4.5760 | 6 | 100% |
| mutation | 4.8863 | 5 | 100% |

The semantic arm cost an estimated $0.5549, including recorded thinking
tokens. Its point estimate improves AUC by about 26.4% against random and
8.0% against the matched edit control. These are descriptive development
comparisons, not statistically established superiority or equivalence.
Targets and seeds were not selected to remove unfavorable agent results.

The oracle is DUT-scoped RTL activity with real AES key-length/direction
execution and per-block reference checks. This is not a gate-power result.
Coverage guidance uses instrumented DUT line coverage, not a named mutation
alias. V4 edits scalar fields only; it does not demonstrate structural
workload synthesis. Cross-design and held-out evaluations are unfinished.

Fifteen early development cells predate full run-manifest capture. The 60
later manifests were copied from the original run outputs without reconstruction.
They include working-tree hashes; the source commit alone is not a complete source
snapshot. Do not present this development panel as a frozen held-out study.

Recompute:

```sh
.venv/bin/python scripts/audit_semantic_archive.py results/aes_transactions_development
.venv/bin/python scripts/summarize_semantic_panels.py results/aes_transactions_development results/aes_transactions_development_matched --out results/aes_transactions_development/comparison.json
```
