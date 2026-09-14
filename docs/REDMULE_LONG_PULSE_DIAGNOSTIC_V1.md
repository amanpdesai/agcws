# Longer-window RedMulE pulse diagnostic v1

Declared after the frozen 9,216-slot long-window baseline search failed bank
admission (2/18 qualified), before new diagnostic measurements. That failure
is preserved; neither targets nor tolerance changes here.

Run eighteen target-independent native workloads: sizes 4/8/16, patterns
zeros/alternating/random, and queued jobs equal to one or two times the minimum
needed for the 1,024-MAC useful-work floor. All use data seed 7500 and a single
phase at cycle 2048, duration 1. Every output of every job must still check.
The observation window remains 262,144 cycles and eight bins.

Extract per-job completion boundaries and activity from the actual traces to
distinguish queue/service time, first-job initialization, steady-job pulses and
operand-pattern effects. These measurements diagnose the proposal/search
limitation; they are not target witnesses or new policy results.

If a pulse-based witness constructor is warranted, freeze its counts, grids,
selection rules and evaluation budget in a separate version before evaluating
any target-directed candidates. Predicted fit never counts as qualification.
No model calls, target replacement, tolerance changes or full-study launch.

The context-v4 source identity first requires an exact replay of the previous
64-program calibration. Numerical endpoints and requested vectors must remain
unchanged; runtime fingerprints are bridged explicitly rather than relabeled.

## Measured outcome

All eighteen cases passed functional and useful-work checks. The archived
`diagnostic.json` records each completion interval and eight-bin activity.
At size 4, the first completion is 368 cycles after release, but later
completions are 1,755–2,022 cycles apart. At size 8 those figures are 1,276
and 2,663–2,666 cycles. These are software-plus-hardware intervals, not isolated
accelerator service times.

Size 16 exposes a modeling hazard: the first completion changes with total
queued job count. Alternating/random operands complete the first job after
6,797 cycles for one job, versus 5,264 for two; zeros take 9,869 versus 8,336.
Therefore translating and adding a single measured one-job pulse is not yet
a justified predictor of a multi-job workload. Inspect program preparation,
release timing and activity alignment before freezing a pulse constructor.
This diagnosis does not qualify additional targets.

Evidence: `results/redmule/long-pulse-diagnostic-v1/`. Its packed archive was
restored and byte-verified (167 files). The new runtime's 64 calibration
programs matched the prior version's integer activity exactly; that separate
568-file archive is `results/redmule/calibration-replay-v4/`.
