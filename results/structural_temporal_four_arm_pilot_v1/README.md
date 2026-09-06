# Four-arm structural temporal development pilot v1

Complete matched-source pilot: two achieved AES reference profiles, seed 310,
16 proposal slots per cell, batch size 4. Random, structural evolution,
complete-schedule agent and alternating hybrid all receive the same schedule
contract and evaluator. The first four schedules are shared random initialization.
All valid simulations perform 64 AES-128 blocks over exactly 6774 clock edges.
The fixed-scale capped NRMSE and tolerance match the preceding CPU pilot.

| Reference | Policy | AUC | Valid slots | Solved |
|---|---|---:|---:|---|
| random_300 | Random | 1.7536 | 16/16 | No |
| random_300 | Evolution | 1.6303 | 16/16 | Yes |
| random_300 | Agent | 1.7536 | 7/16 | No |
| random_300 | Hybrid | 1.7536 | 8/16 | No |
| random_301 | Random | 1.5556 | 16/16 | Yes |
| random_301 | Evolution | 2.0152 | 16/16 | No |
| random_301 | Agent | 2.0103 | 6/16 | No |
| random_301 | Hybrid | 2.0152 | 8/16 | No |

The agent's 13/32 valid slots include eight random initializers: only 5/24
model-proposed slots were valid. Hybrid validity similarly includes its CPU
batches. Do not interpret its 16/32 total validity as model schema compliance.
Neither agent arm solves a target in this pilot. There is no model advantage.

Two model responses hit MAX_TOKENS after emitting long explicit repetitive
schedules. Other invalid proposals violate the exact work/idle totals despite
schema-valid JSON. No failed proposal was repaired or retried for free; all
128 requested slots and all provider-reported usage remain in the ledgers.
The pipeline audited loss, AUC, censoring, work/window invariants, validity
stages, token totals and configured-rate cost before copying these artifacts.

Recorded model cost is $0.0928945, with no unknown-usage batches in this panel.
The preceding eight-slot diagnostic smoke cost $0.0063058 separately. This
tiny one-seed panel is interface diagnosis, not a confirmatory comparison.
The target-manifest wording "no agent ... claim" means no agent-effectiveness
claim; these agent/hybrid ledgers contain real Vertex calls and captured model
versions, prompts and usage.

Do not scale this full-schedule interface yet. The next development candidate
should propose compact typed structural edits through the same budget-preserving
operators available to the CPU baseline. Unlike the old scalar patch interface,
those operators must name explicit parents and legal sequence operations,
not arbitrary nested JSON paths. Preserve this failed candidate as evidence.
