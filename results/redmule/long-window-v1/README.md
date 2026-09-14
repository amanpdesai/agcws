# RedMulE longer-window v1 — qualification failed

[Frozen protocol](../../../docs/REDMULE_LONG_WINDOW_V1.md): 262,144 cycles,
eight bins, unchanged RTL and functional checks. This does not replace the
original 65,536-cycle bank or delete any failed request.

Fresh calibration completed all 64 proposals: **58 valid, six USEFUL_WORK
rejections**. The 5th/95th percentile envelope is
1.999969482421875–27.53013916015625 transitions per edge; scale
25.530169677734374. This is activity, not watts.

`requested_bank.json` fixes eighteen requests (eight shapes plus control in
each split) before witness search. All nonflat requests pass the >0.12
constant-vector-floor gate. No target is admitted from that diagnostic alone.

The development and confirmation configs run phase-random and phase-GA at
256 proposals per request/arm. Both panels completed all 4,608 slots each.
Independent target-qualification audits admit **1/8 nonflat requests and 0/1
controls per split**: development burst and confirmation quiet interval only.
All 9,216 attempts remain archived. The longer window and the frozen baseline
search do not establish the required bank; this is not proof of infeasibility.
No LLM calls or full paper run have been launched for this version.

Parallel calibration premeasurement preserves the ordinary random proposal
sequence and all 64 charged slots. Its receipts and compute time are retained
inside the calibration archive, rather than treating cache hits as free work.

Regression checks: full suite 686 passed with three existing warnings;
the subsequent parallel-proposal equivalence test separately passed.
