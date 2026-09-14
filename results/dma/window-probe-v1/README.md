# DMA timing corners — replacement window selected, not yet applied

All twelve [frozen cases](config.json) completed with correct 4,096-byte transfers.
The [predeclared rule](../../../docs/DMA_WINDOW_CORRECTION.md) selects **9,216
cycles**: latest schedule end 8,947.5, plus 256 guard cycles, rounded upward to a
multiple of 128. Timing by transfer-group size is independent of the three tested
wait placements:

| Group size | Declared schedule end (cycles) |
|---|---:|
| 1 | 8,947.5 |
| 2 | 8,051.5 |
| 4 | 7,603.5 |
| 8 | 7,379.5 |

This is why using the random corpus's maximum of 7,771.5 would have been unsafe.
The current random generator only partitions work into at most 16 groups; these
corners include 32 and 64. The paper baseline should cover the full legal group
range before its settings are frozen. This is a proposal-distribution limitation,
not evidence that the validators give policies different legal languages.

`evidence/` contains the manifest, all twelve native programs, measured outcomes,
functional records, activity arrays and `audit.json`. Packing restored and
hash-checked 101 exported files. The audit reconstructs all eight bins and checks
cache identity, exact transfers and timing units. It records a candidate window,
not qualification under that window or exhaustive timing coverage of the DSL.

Next: apply a new DMA measurement version after live source-frozen runs finish;
replay these corners, regenerate calibration and qualify fresh requested banks.
The old v2 evidence remains unchanged. No paid comparison is authorized by this
diagnostic.
