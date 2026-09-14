# AES target qualification v2

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
[confirmation qualification](confirmation-qualification.json) each admit 7/8
non-flat requests, but neither control passes. Development quiet-interval error
is 0.1338; confirmation activation error is 0.1190. Control errors are 0.1023
and 0.1107, respectively, above the unchanged 0.10 tolerance.

Per-split archives in `development/` and `confirmation/` preserve every attempt;
packing verified restored file hashes. This bank is not ready for the full study.
