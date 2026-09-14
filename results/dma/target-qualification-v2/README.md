# AXI DMA target qualification v2

[Requested bank](requested_bank.json), [development config](development.json),
[confirmation config](confirmation.json). Vectors were committed before search.
All eight non-flat families pass the necessary constant-vector-floor check;
none is admitted until a valid measured witness reaches tolerance.

The [frozen procedure](../../../docs/TARGET_QUALIFICATION_V2.md) preserves the
v1 measurement contract and calibration, strengthens contrast, and separates
development timing from confirmation timing. Phase-random and phase-GA each get
256 proposals per request, two-slot batches, no early stopping. Seeds are 7800
and 7900. Both searches completed 4,608 slots.

[Development qualification](development-qualification.json) and
[confirmation qualification](confirmation-qualification.json) each admit 3/8
non-flat requests: deactivation, burst and rise-fall. Activation, quiet interval,
alternating, ramp and irregular remain unqualified. Neither control passes:
errors are 0.1330 and 0.1498, respectively, above the unchanged 0.10 tolerance.

Per-split archives in `development/` and `confirmation/` preserve every attempt;
packing verified restored file hashes. These misses are not proof of infeasibility,
and the bank is not ready for the full study.

## Window audit

[Development](development-window-audit.json) and
[confirmation](confirmation-window-audit.json) audits reconstruct all eight rates
from activity samples and check completion, cache identity and exact work counts.
They cover 2,154 and 2,183 distinct valid workloads within their respective splits.
The latest declared schedule end is cycle 7,771.5 / 7,743.5, respectively, leaving
at least 4,228.5 / 4,256.5 padded cycles in the 12,000-cycle observation window.
Every measured workload has bin 7 at 2.0 transitions/edge and bin 8 at
1.9993333333333334. The small final-bin offset is common to all workloads.

Thus the existing corpus cannot exercise the full requested temporal horizon.
This is not a theorem about every legal program, but it identifies a concrete
window/DSL mismatch rather than evidence that an agent cannot shape DMA activity.
Further local refinement on this contract is paused. Correcting the observation
contract requires versioned calibration and qualification, not reinterpreting
these measurements or quietly changing the existing target vectors.
