# Common bit activity — independent verification

Contract: [known-bit-activity v2](../../docs/BIT_ACTIVITY_ALIGNMENT_V2.md),
supplementing the [frozen qualification procedure](../../docs/BIT_ACTIVITY_V1.md).

[Eight schedule recounts](independent-schedule-recount.json) match native bit
rates and clock counts exactly: confirmation burst and flat control for AES,
DMA, mesh and RedMulE. The independent reader uses a separate implementation.

[Three Ibex recounts](independent-ibex-recount.json) match transition totals,
rates, clock counts and marker bounds exactly. The reference is the historical
time-bin counter from commit 16112b133, recorded with its source hash; it does
not call the new common counter. Cases are calibration-18, confirmation burst
and confirmation flat control. These traces have known carried state; this
check alone does not validate mixed-X masking, which has separate unit tests.

These checks establish measurement consistency on the selected traces, not
capacitance weighting, gate-power prediction or signoff power. Waveform hashes
identify what was recounted; raw traces remain local scratch.

Per-design requalification evidence is under `results/<design>/bit-activity-v2/`.
AES, DMA, Ibex and RedMulE have completed. Mesh witness searches are in progress;
the overall scientific launch hold remains until their disposition is audited.
