# AXI DMA target qualification v2

[Requested bank](requested_bank.json), [development config](development.json),
[confirmation config](confirmation.json). Vectors were committed before search.
All eight non-flat families pass the necessary constant-vector-floor check;
none is admitted until a valid measured witness reaches tolerance.

The [frozen procedure](../../../docs/TARGET_QUALIFICATION_V2.md) preserves the
v1 measurement contract and calibration, strengthens contrast, and separates
development timing from confirmation timing. Phase-random and phase-GA each get
256 proposals per request, two-slot batches, no early stopping. Seeds are 7800
and 7900. Searches are in progress; no completed qualification result is claimed.
