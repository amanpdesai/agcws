# Current-runtime Ibex bank admission

All eighteen selected witnesses reproduce their numerical profiles, allocation,
execution and feedback. Architectural reference checks and target qualification
were recomputed. The new public bank is `../qualified-bank-v1.json`; it contains
target vectors and witness identifiers, not witness programs.

The paired calibration bridge is `../calibration-replay-v3/`, with all 64 cases
matching full decoded waveforms after excluding only header date metadata.
The bank records lineage to that receipt and the original 216-attempt panel.

Protocol: [IBEX_BANK_ADMISSION_V1](../../../docs/IBEX_BANK_ADMISSION_V1.md).
The compact replay archive restores 272 files with verified hashes. The three
compressed sidecars restore the frozen parent config/spec/freeze without
checking hundreds of kilobytes of repeated execution data into readable JSON.

Bank qualification is complete; the bounded all-target Flash feedback smoke
is running separately. Full-study readiness remains false.
