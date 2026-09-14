# Fixed-work witness refinement — development plan

Status: AES v3 procedure fixed before execution; run manifests pin these sources
and the selected v2 parents. DMA execution is excluded pending its window audit.

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

The AES v3 runner first replays each selected parent exactly (one charged slot).
Already-qualified parents stop there. Otherwise, three explicit target-guided
initializations allocate the 64 work units by largest remainder of target rate
above the calibrated idle baseline. Estimated unit duration is
`(6774 - 6000) / 64`; the residual per-bin durations allocate the 6,000 waits.
Three candidates put each bin's waits after, half before/after, or before work.
All three are measured and charged before selecting an improvement. This timing
estimate only proposes candidates; measured profiles decide admission.

Unqualified incumbents then receive the 128 paired steps, giving a maximum of
260 charged slots per request. Seeds are 8300 development and 8400 confirmation;
18 request workers run concurrently. Stop only after a complete seed/paired batch
passes the unchanged qualification gate. Strictly smaller measured target error
selects incumbents; ties retain the earlier candidate. Frozen replay mismatch or
unknown infrastructure failure stops the run, never substitutes a score.

The runner and helper hashes, parent manifest hashes, requested bank, initial
candidates, budget and measurement provenance are frozen before execution.
Keep development/confirmation
qualification costs separate from later policy budgets. Audit restored archives
against paired decisions, native validity, measurement identity and bin arithmetic.
Do not edit measurement sources while the current Ibex qualification is live.

DMA's v2 timing audit found more than 4,200 padded cycles after every measured
schedule; the last two bins have no workload-dependent activity in either split.
It is excluded from this refinement version. A new DMA observation contract
requires new calibration and fresh qualification, with the old evidence retained.

## Interpretation limits

These searches establish feasible benchmark requests, not policy superiority.
Retain all v2 failures and all new unsuccessful proposals. A remaining miss can
reflect insufficient search, an unsuitable schedule representation, fixed-window
overhead, or an infeasible request; none is established by the miss alone.
