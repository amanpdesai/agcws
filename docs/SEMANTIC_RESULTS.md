# Held-out semantic search results

Completed 2026-09-05. The selected agent is competitive descriptively with
random on AES, but parity is not established. Random has lower mean AUC on
DMA. There is no supported cross-design superiority claim over random or
AES coverage-guided search.

## Evidence and method

[The complete report](../results/semantic_heldout_comparison.json) contains
550 cells and 27,500 proposed slots, with audited ledgers, original run
manifests and input artifact hashes. AES has six policies; DMA has five.
Each policy uses five targets (0.10, 0.25, 0.50, 0.75, 0.90), ten held-out
seeds (200–209), 50 slots, batch size 4 and epsilon 0.02. Invalid and missing
proposals consume slots. Both designs retain hard useful-work floors.

The [predeclared protocol](HELD_OUT_PROTOCOL.md) selected semantic-edits-v4
over semantic-catalog-v5 using all 30 development cells per candidate,
balanced across AES and DMA. The same Gemini 2.5 Flash controller, prompt and
sampling configuration were frozen before evaluation. No held-out tuning,
per-design controller choice or exclusion of failed proposals was performed.
Every held-out source/configuration manifest passed the freeze comparison.

AES uses the transaction harness; DMA uses the pipelined harness. Old
calibrations and legacy harness results are not pooled with this study.
These runs used host tools, not the newly introduced Docker wrapper.

## Primary endpoint first

Mean best-so-far normalized-error AUC, lower is better. Secondary columns
are descriptive; they do not replace the primary endpoint. Each row has
50 runs and 2,500 proposal slots.

| Design | Policy | Mean AUC | Solved | Capped evaluations-to-target | Valid proposals |
|---|---|---:|---:|---:|---:|
| AES | Random | 2.2393 | 38/50 | 26.06 | 100.00% |
| AES | Mutation | 4.5159 | 18/50 | 35.88 | 99.80% |
| AES | Evolutionary | 4.5674 | 23/50 | 35.28 | 99.96% |
| AES | Scalar-edit evolution | 3.5316 | 42/50 | 23.26 | 74.16% |
| AES | Coverage-guided line | 3.3627 | 23/50 | 34.52 | 99.80% |
| AES | Semantic-edits-v4 | 2.1938 | 43/50 | 18.62 | 74.88% |
| DMA | Random | 2.0849 | 38/50 | 25.56 | 100.00% |
| DMA | Mutation | 4.0012 | 22/50 | 36.50 | 100.00% |
| DMA | Evolutionary | 3.2367 | 33/50 | 30.64 | 99.60% |
| DMA | Scalar-edit evolution | 6.5367 | 14/50 | 40.92 | 22.92% |
| DMA | Semantic-edits-v4 | 2.6507 | 36/50 | 24.32 | 74.72% |

Unsolved runs contribute 50 to capped evaluations-to-target and remain
right-censored. This column is not an estimated mean time to eventual success.

## Paired inference

Differences are agent minus baseline AUC. Five target differences are averaged
within each seed before analysis: ten seed units, not fifty independent
observations. Intervals use the fixed 10,000-replicate seed bootstrap; p-values
use exact two-sided sign flips with Holm correction across all nine tests.
The displayed 95% intervals are pointwise, not simultaneous intervals.

| Design | Baseline | AUC difference | Bootstrap 95% interval | Holm p | Agent superiority |
|---|---|---:|---|---:|---|
| AES | Random | -0.0455 | [-0.6579, 0.6310] | 0.8965 | No |
| AES | Mutation | -2.3222 | [-3.5411, -0.9424] | 0.0879 | No |
| AES | Evolutionary | -2.3737 | [-3.6833, -0.8742] | 0.0879 | No |
| AES | Scalar-edit evolution | -1.3378 | [-2.6164, -0.4300] | 0.0684 | No |
| AES | Coverage-guided line | -1.1689 | [-1.7795, -0.5366] | 0.0820 | No |
| DMA | Random | 0.5658 | [0.0787, 1.0669] | 0.1992 | No |
| DMA | Mutation | -1.3506 | [-1.9634, -0.7365] | 0.0313 | Yes |
| DMA | Evolutionary | -0.5861 | [-1.1209, -0.0798] | 0.1992 | No |
| DMA | Scalar-edit evolution | -3.8860 | [-4.7317, -3.1580] | 0.0176 | Yes |

Only the DMA mutation and scalar-edit comparisons support agent superiority
under this protocol. Nonsignificance elsewhere is not equivalence. The
matched scalar-edit baseline's poor DMA legality limits what beating it
establishes; random is the more demanding comparator.

## Validity and cost

AES agent failures: 561 schema, 43 protocol, 0 functional, 24 useful-work.
DMA agent failures: 446 schema, 179 protocol, 0 functional, 7 useful-work.
These are proposal-slot counts, including missing/malformed proposal slots;
they must not all be interpreted as simulated hardware failures. The complete
JSON reports the stage breakdown for every baseline as well.

Recorded agent usage: AES 1,806,454 input / 506,000 output tokens, estimated
$1.8069; DMA 3,290,303 input / 620,168 output tokens, estimated $2.5375.
Three AES and five DMA batches have unknown provider usage. The combined
$4.3444 is incomplete configured-rate accounting, not a billing reconciliation.
CPU baseline LLM cost is zero; that does not mean CPU computation is free.
Shared-host concurrency changed for DMA CPU runs and is documented in their
archive; wall-clock measurements are not a controlled runtime comparison.

## What improved, and what remains unproven

Development identified a better balanced controller (v4 mean AUC 2.0595,
v5 3.1320); held-out evaluation supports improvements over two DMA baselines.
It does not show the hoped-for general advantage over random. The AES
development advantage over random shrank to a small held-out difference.
No seeds, targets or controllers were added after inspecting these findings.

The selected controller edits existing scalar fields. It cannot insert,
delete or reorder workload structure, so this is not proof of greater workload
expressiveness. Hand-written matched-window AES temporal schedules establish
controllability separately, not an agent result. RTL activity targeting also
does not establish gate-power prediction: proxy-to-gate validation remains open.

The next research question is structural/temporal synthesis at matched useful
work and measurement windows, with the same richer representation and budget
available to classical policies. That requires a new development protocol and
fresh held-out seeds, not tuning against this now-observed evaluation panel.
