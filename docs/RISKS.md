# Risks

## R-01 — Liberty lacks usable power characterization — H

Inspect `internal_power`, rise/fall power, leakage, capacitance, and cell coverage by D3. If incomplete, report synthesis-weighted switching power.

**Initial inspection (2026-08-30).** Candidate Sky130 HD typical-corner Liberty:
`/opt/eda/ChipSTA/test/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib`. It is 12.8 MB
and contains 2,477 `internal_power`, 2,477 `rise_power`, 2,477 `fall_power`,
429 `cell_leakage_power`, and 4,406 `capacitance` occurrences. This is promising
but does not close R-01: coverage must still be compared with the synthesized
netlist cell histogram, and the path must be supplied through `AGCWS_LIBERTY`.

**Closed (2026-08-31).** The copied Sky130 Liberty contains 2,477 internal-power
groups, 2,477 rise-power tables, 2,477 fall-power tables, 429 leakage entries,
1,328 capacitance entries, and 6 clock-gating declarations. The AES Sky130
netlist uses 72 distinct cell types and 43,619 instances; all are defined by
the Liberty (100% instance coverage, no unmatched types). The independent
Nangate45 netlist likewise has 100% instance coverage (29 types, 40,479
instances). R-01 is closed for relative synthesis-level power claims; this does
not constitute signoff-accuracy power characterization.

## R-02 — Activity annotation coverage — H — OPEN

The verified AES Sky130 run reports 203 VCD-annotated pins and 153,856
unannotated pins, a pin-count fraction of 0.0013177. This is far below a
threshold suitable for claiming broad gate-level activity agreement.

**Fallback currently in force.** Report synthesis-weighted switching power and
RTL cycle-toggle profiles; do not describe the result as signoff-accuracy power.
The next resolution step is hierarchy-preserving name mapping or gate-level
simulation of finalists, followed by a per-design proxy-to-gate rank analysis.

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
