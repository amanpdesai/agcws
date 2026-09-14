# Marker alignment correction v2

2026-09-14, before corrected remeasurement. Preserve `out/bit-activity-v1`.
The first implementation of the common counter uses rising-edge sample
ownership even for an explicitly marker-bounded interval. Ibex's retired marker
can fall between rising edges (observed begin286, first rising edge287).
This shifts boundary ownership and can omit pre-first-edge events. One inspected
calibration case differs from the previous marker-based bit count by one bit.

Correct explicit marker windows to assign events using
`floor((timestamp - begin) / period)`, retaining the half-open interval and
requiring its duration to equal `cycles * period`. Full-trace schedule backends
keep rising-edge sample ownership. The clock count, scopes, initialization
rules, target families, qualification thresholds and fixed input programs are
unchanged. Record contract `known-bit-activity-v2`.

Add a regression where a marker lies on a falling edge and transitions occur
at each bin boundary. Optimize all-known binary decoding without changing
values or masks; test both known and mixed-known vectors. Do not modify a live
replay's runtime source. Freeze fresh manifests after this correction and run
the same 82 cases per design in `out/bit-activity-v2` before admission.

The CPU qualification procedure remains `BIT_ACTIVITY_V1.md`, supplemented by
this implementation correction. No old scale is transferred and no target is
softened. Previously prepared AES targets are diagnostic v1 evidence, not the
new-runtime bank. No model calls or comparative panel are authorized.
