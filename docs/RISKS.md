# Risks

## R-01 — Liberty lacks usable power characterization — H

Inspect `internal_power`, rise/fall power, leakage, capacitance, and cell coverage by D3. If incomplete, report synthesis-weighted switching power.

## R-02 — Activity annotation coverage — H

Report annotated-net and annotated-capacitance fractions. Preserve hierarchy, use rank correlation, or gate-level simulate finalists if coverage is poor.

## R-03 — Scalar targeting is trivial — M

Measure evaluations-to-target by D9; make compositional/temporal arms primary if scalar search has no signal.

## R-04 — Hierarchy loss — H

Preserve selected synthesis boundaries; otherwise restrict composition to surviving regions or report RTL-only composition.

## R-05 — Temporal trace size — M

Use 8–32 coarse windows, bounded workloads, and split/online activity.

## R-06 — Idle low-power solutions — M

Require `useful_work()` floors and report energy per operation secondarily.

## R-07 — Unfair baseline — H

Same DSL, budget, checker, history, and batch semantics for every policy.

## R-08 — Proxy exploitation — M

Use hidden gate-level validation and report proxy-to-gate regressions.

## R-09 — Ibex toolchain tail — M

Start early; cut Ibex by D15 if it is not operational.

## R-10 — $300 credit exhaustion — L

Batch LLM candidates and defer multi-seed repetition to the free compute window.

## R-11 — Prior-art surprise — H

Check SAT/ILP maximum-power estimation and burn-in vectors by D5.
