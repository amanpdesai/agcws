# Exploratory precision pilot — tolerance 0.05

2026-09-15: user requests an immediate tighter-threshold pilot after observing
the 0.10 pilot. This is post-hoc exploration, not a new confirmatory study.
Preserve the original run unchanged. Do not select a paper headline between
these thresholds after seeing results.

Same Ibex alternating vector, calibration, source/runtime identity, two seeds
9500–9501, four arms, 128 slots, batch two, eight cell workers and two provider
workers. Change only tolerance to 0.05 and the authorized cost remainder.
Launch fresh trajectories in a separate directory; do not splice old LLM
responses into them. Retain failures, exhausted budgets and terminal-best AUC
completion. This answers exploratory performance at tighter tolerance, not
an isolated causal threshold effect on stochastic model outputs.

Original model cells are terminal, with liability $1.9836561. Set this pilot's
shared estimated-liability ceiling to $8.01, keeping combined authorized
liability below $10. Unknown calls retain reservations. No automatic increase,
restart or model substitution. The meter is not a Google billing hard limit.

The target has constant-vector floor 0.4 and high–low swing 0.8 calibration
units. At 0.05, allowed RMS error is 6.25% of that swing. Nonflatness is proven;
broad task hardness is not established by this one exposed target.

Session: `agcws-ibex-precision-v1`. Runner and log:
`scripts/run_ibex_precision_pilot.sh`, `out/ibex-precision-pilot-v1/runner.log`.
No full five-design study is authorized by this pilot.
