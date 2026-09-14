# Fixed-work witness refinement — development plan

Status: proposal operator tested; runner and frozen execution manifest pending.
No new qualification search has been launched under this procedure.

## Evidence motivating the change

AES v2 qualifies seven non-flat requests per split but neither flat control.
DMA v2 qualifies only deactivation, burst and rise-fall in either split. All
requests retain the original v2 vectors and 0.10 tolerance. See the per-design
qualification reports linked from RESULTS.md for every failure.

Both backends require exactly 64 work units and 6,000 idle cycles. AES lowers a
work unit to one encrypted block. DMA lowers it to one 64-byte transfer; a work
group issues at most eight concurrent transfers and waits for each group to
complete. Consequently splitting a DMA work group can change execution duration
and concurrency: it is not a semantics-neutral normalization of the measurement.
The observation horizons remain 6,774 AES cycles and 12,000 DMA cycles.

## Next measured qualification pass

Use the best valid measured v2 parent for each request, with exact replay before
refinement. Transfer idle cycles between wait positions, or work units between
work positions. Evaluate both signs of each edit from the same incumbent before
selecting an improvement. This preserves exact resource totals while moving
activity in time. Zero/negative sizes are not repaired: the native validator
rejects them and they remain charged proposals.

The tested operator in `analysis/schedule_refinement.py` uses deterministic
coordinate selection and 128 paired steps. Idle steps are 256/64/16/4/1 cycles
over batches 0–15/16–31/32–63/64–95/96–127; work transfers move one unit.
It cannot create new work/wait positions. Any balanced initialization or structural
split must therefore be an explicit, measured and charged proposal, not a hidden
rewrite of a parent. In particular, an equal-allocation control is a candidate,
not a witness until its measured profile passes both control gates.

Before execution, freeze the runner, parent evidence hashes, candidate schedule,
seed assignment, exact budget and stop rule. Keep development/confirmation
qualification costs separate from later policy budgets. Audit restored archives
against paired decisions, native validity, measurement identity and bin arithmetic.
Do not edit measurement sources while the current Ibex qualification is live.

## Interpretation limits

These searches establish feasible benchmark requests, not policy superiority.
Retain all v2 failures and all new unsuccessful proposals. A remaining miss can
reflect insufficient search, an unsuitable schedule representation, fixed-window
overhead, or an infeasible request; none is established by the miss alone.
