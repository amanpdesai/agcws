# Common bit-activity contract v1

Frozen procedure before new measurements, 2026-09-14. This is CPU-only task
engineering, not a model study. Preserve v6 and all historical evidence.

## Measurement

Count Hamming-distance transitions between known bit values, once per unique
VCD identifier. Normalize shortened binary values to declared width; equivalent
bus/scalar declarations must agree. Exclude parameter declarations and the
explicit clock identifier, including its aliases. Keep existing design scopes
and Ibex's explicit CSR exclusion; do not pretend these are identical physical
subsystems. Record scope, exclusions, widths, timescale and contract version.

Require one explicitly named clock, uniform rising-edge spacing and the exact
design observation length. Never substitute signal events for missing clocks.
Group all events at one timestamp before assigning them to a cycle so waveform
line ordering cannot change bin ownership. Bins use `floor(k*N/8)` sample
boundaries. Keep the existing reset-inclusive schedule windows and Ibex's
half-open marker window; neither duration nor reset policy changes silently.

Unknown initial bits may become known during reset/first use in the schedule
backends. That initialization is recorded but is not counted as a physical
transition. Count transitions only on bits known at both endpoints. A bit that
has become known must not become unknown again: reject that observation, with
a diagnostic, rather than reward X activity. Report remaining unknown bits;
do not call them zero-valued or evidence of full physical activity coverage.
Ibex retains its stricter requirement of known carried state at window start.
Unknown clock values after initialization, inconsistent widths, malformed
values, time reversal and incomplete observations are errors, not fallbacks.

This remains unweighted RTL bit activity, not watts or timing-aware glitch power.

## Calibration and qualification

Freeze the existing 64 calibration programs and eighteen selected witness
programs per design before remeasurement. Reuse those programs, not their
scores. Preserve invalid attempts. Require at least 32 valid calibration
observations; independently recompute inclusive 5th/95th bin percentiles and
median whole-window mean. Nonfinite or degenerate calibration fails the design.

Generate eighteen fresh requested vectors using the existing analytic families:
the v2 fixed-work construction for AES/DMA and v1 construction for the other
three, with the newly measured scale. Freeze these vectors before inspecting
witness errors. Never convert an old event target by a fitted scale factor.
Tolerance remains 0.1, nonflat constant-vector floor >0.12, and controls require
both target and achieved floor <=0.1. Report all pairwise distances/cross-solves.

First test each corresponding old witness against the new target. This is one
explicitly charged feasibility attempt per request, not a comparison policy.
For missed requests whose necessary floor passes, run phase-random and phase-GA
at 256 proposals each, batch two, no early stopping, using development seed7300
and confirmation seed7400. Reusing these engineering seeds is explicit; no
unseen-task claim follows. These are new-metric runs, not extensions of old runs.
Choose the lowest valid error, ties by policy then proposal index. Retain every
miss and invalid attempt; no target replacement or extra search within v1.

Successful banks get new versions and current runtime fingerprints. Failed
banks remain failed with diagnosis and a proposed separately versioned remedy.
No LLM calls, full comparative panel or automatic promotion of full-run plans.
Use bounded process concurrency and preserve compact measurements while managing
large waveform scratch explicitly; do not exhaust disk by retaining every trace.
