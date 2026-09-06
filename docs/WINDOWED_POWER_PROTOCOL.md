# Windowed gate validation — v1

Declared before evaluating windowed finalist power. This is post-search,
descriptive validation, not a new policy-selection or held-out superiority test.

## Cases and oracle

Use exactly the sixteen seed-400 finalists in
`results/structural_temporal_finalists_v1.json`, without substitutions. Also
evaluate the two original achieved reference schedules per design from the
frozen AES/DMA verification corpora. References define power-valued targets;
the search's activity vectors are not watts. No new agent calls or tuning.

Reuse matched finalist waveforms and netlists. Reference GLS must match its
original RTL schedule, functional checks and observation horizon. Use upstream
OpenSTA `a9a3f30ca97dc13f9ef911cae1a82c42c67379e1`, the existing Sky130 HD
TT Liberty, and unchanged zero-delay functional models. Record input hashes.

## Boundaries

The search partitions N rising-edge samples at indices floor(k*N/8). Place
each internal power boundary one VCD tick before that indexed rising edge,
and reject a trace if any timestamp occurs at that proposed boundary. Because
the boundary is event-free, OpenSTA's inclusive endpoints cannot duplicate a
transition. Preserve the trace's actual first and last timestamps. The eight
physical durations sum exactly to the full span; record them rather than
pretending all bins have identical duration. The short leading/trailing
fractions of a cycle are included in the first/last bins. Reset remains included.

Verify the clock count and period, units, monotone timestamps, empty boundaries,
and identical RTL/GLS grids. Test independent transition and high-time counts
on known traces, including boundary-adjacent events and carried-in state.
Use a fresh OpenSTA process per window, not stale activity from another read.

## Measurements and checks

For each of eight windows and the full trace, retain internal, switching,
leakage and total power, pin annotation counts, Tcl invocation and tool output.
Dynamic power is internal plus switching. Annotation must match the full trace.
The duration-weighted switching mean must agree with the full-window switching
estimate within relative 1e-5 (absolute 1e-12 W). This checks an additive quantity.
Report the internal/dynamic discrepancy separately: conditional internal-power
estimation can be nonlinear in averaged activity, so it is not an exact physical
energy-conservation test. Do not force that discrepancy to zero.

### Precision correction discovered on the first case

The first AES case failed the native aggregate switching check by 20.78 ppm.
OpenSTA's `PowerResult` accumulates cell powers in float32. Independently
re-summing its 22,901 leaf values with Python `math.fsum` reduced the relative
discrepancy to -1.602e-8, without changing activities, durations or cells.
Use a double-precision sum of native leaf switching values for the additive
check, at the unchanged tolerance. Retain the original design-total reports
and use those original totals for reported profiles. This changes numerical
verification, not target normalization or case selection. The failed initial
run and independent precision diagnostic remain under `out/window-power-v1/`;
the production measurements use a separate `measurements/` directory.

## Descriptive endpoint

Let P_i be finalist dynamic power, R_i the achieved reference's gate dynamic
power, and d_i the matched duration of window i. Report

`gate_NRMSE = sqrt(sum(d_i*(P_i-R_i)^2) / sum(d_i*R_i^2))`.

The reference denominator is fixed for all policies on that design/target;
there is no candidate-peak normalization. Reject zero/nonfinite reference RMS.
Report raw watt vectors and duration-weighted means alongside this statistic.
No new gate-level solved threshold or inferential p-value is introduced.
Retain original activity errors and their original normalization separately.

## Claims and writing

Windowed validation can establish measured gate-profile agreement for these
selected cases, not a power-guided agent advantage or general proxy validity.
These reference targets were previously observed, and the cases are selected
finalists, not an unbiased new corpus. No cross-design pooled correlation.

The paper must retain the significant temporal AES agent loss and the scalar
AES nonsignificant numerical agent advantage. SCHEMA includes typed-edit
contract errors, not just malformed JSON. Adapter abstraction may reduce
protocol-reasoning demands, but its causal effect is not measured here. Neither
fixed work nor a shared legal grammar mathematically guarantees fixed energy
or explains the method ordering by itself.
