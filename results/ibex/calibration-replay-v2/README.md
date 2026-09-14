# Full Ibex calibration waveform replay

All 64 original calibration cases were replayed, including the three rejected
workloads. The strict raw-file comparison matched only those three rejections:
valid FST recordings have different creation-date metadata.

The separately declared whole-waveform comparison matched **64/64 cases** after
excluding only the decoded VCD header `$date` block. Signal declarations,
timestamps and every signal value were compared, not just the eight-bin sums.
Raw waveform hashes and excluded dates remain in the packed `waveform-audit.json`.
Valid profiles, CPU state, workload allocation, execution and feedback also
match. This explains the raw-file mismatch; it does not hide it.

Protocol: [IBEX_CALIBRATION_REPLAY_V2](../../../docs/IBEX_CALIBRATION_REPLAY_V2.md).
The replay manifest identifies its runtime. Subsequent source changes need an
explicit compatibility bridge; this archive alone does not assert current
five-design study readiness.
