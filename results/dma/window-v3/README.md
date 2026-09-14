# DMA window v3 — all eighteen requests witnessed

The new measurement uses 9,216 cycles and the full legal random group-count
range, under the refreshed source inventory. All twelve timing corners remain
functionally valid. Their measured activity arrays and timing units pass the
new-window audit in `corner-evidence/`; this is a real replay, not a truncated
reinterpretation of old traces.

[Calibration](calibration.json) includes all 64 proposals, all valid. The frozen
5th/95th-percentile bin endpoints are 1.9991319444 and 14.0358940972 transitions
per edge, with scale 12.0367621528 and median whole-window mean 7.0695529514.
`calibration-evidence/` preserves the original trials and source manifest.

[Requested targets](targets/requested_bank.json) use the existing v2 analytic,
fixed-mean construction on this new calibration. All eight non-flat families
pass their necessary floor gate in each split. All eighteen requests now have
valid measured witnesses in [the admitted bank](../qualified-bank-v1.json).
The generated phase-random/GA configs are available but have not been executed
on this bank; do not mistake configurations for results.

The separately [declared serialized witness pass](../../../docs/DMA_SERIAL_WITNESSES_V3.md)
executed [54 fixed proposals](serialized-config.json), three per request,
through the same native backend. It is CPU qualification, not a paid or held-out
policy study. Old window-v2 results remain unchanged in their own archive.

All 54 proposals pass the functional gate. Selected witness errors range from
0.0033 to 0.0232, below the unchanged 0.10 tolerance. The serialized constructor
produced these witnesses, not an agent. `serialized-evidence/` retains all
attempts and the qualification report; packing restored and hash-checked 416
files. Full-study readiness still requires live Flash and baseline loop smokes.
