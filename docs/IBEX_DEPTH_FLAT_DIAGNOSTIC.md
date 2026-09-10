# Retrospective depth-target difficulty

2026-09-10, post-hoc re-analysis only. The original study, endpoints and aggregate
are unchanged. Best constant-vector error is population standard deviation of
the target rates divided by the frozen scale, against tolerance 0.1.

| Target | Constant-vector floor | Requires nonconstant output | Pro solves / 3 | Random solves / 3 |
|---|---:|---|---:|---:|
| 0 | 0.45304 | Yes | 3 | 0 |
| 1 | 0.03326 | No | 3 | 3 |
| 2 | 0.38993 | Yes | 3 | 0 |
| 3 | 0.29854 | Yes | 3 | 0 |

Nine of Pro's twelve solves necessarily required nonconstant activity. Random
and coverage solved zero of those nine cases; Flash solved four. This sharpens
the development finding, not its statistical status: three development seeds
remain development evidence. A flat vector inside tolerance does not prove a
legal program can realize that exact vector, nor invalidate an observed solve.

[Machine-readable diagnostic](../results/ibex_depth_flat_diagnostic_v1/summary.json)
records input manifest and aggregate hashes. Reproduce with
`python -m analysis.ibex_depth_flat_diagnostic`.
