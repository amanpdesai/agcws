# Historical baseline panel retirement

The user stopped the original `baselines-maxbin-v1` panel on 2026-09-16 to
restart all arms from a clean implementation state. It completed **824 of 900
cells**, not the full matrix: AES/DMA/mesh/RedMulE 180 each, Ibex 104. The Ibex
runner recorded exit code -15 after requested termination.

[Stopped-panel inventory](stopped-panel.json) records the original manifests,
per-design compact-archive SHA-256 hashes, byte sizes and member-index hashes.
The large archives remain **local** under `out/retired-baselines-maxbin-v1/`;
this Git directory is an index, not a claim that their contents are published.
Every compact archive member was verified before waveform deletion began.
Original compact records remain locally available as well.

Waveform retirement is a separate operation. Its authoritative completion
receipt is `out/retired-baselines-maxbin-v1/complete.json`; do not infer cleanup
completion from the existence of this stopped-panel inventory. Expanded VCDs
are deleted only after exact reconstruction from retained FST/zstd data is
verified. Per-waveform receipts record both hashes. No unique waveform or
compact evidence is intentionally discarded.

Neither results nor evaluation caches from this incomplete panel enter the
new `baselines-model-v1` panel. The same previously observed target bank is used,
so the new panel is post-hoc robustness work, not fresh held-out confirmation.

## Cleanup completed and independently audited

[cleanup.json](cleanup.json) records **42,081 VCDs / 7,013,915,049,008 raw bytes**
retired. Every planned source VCD is absent; every retained compressed waveform
matches its receipt's SHA-256 and length. All five compact archives, member
indexes and historical manifests still match the stopped-panel inventory, and
the completed-cell counts remain unchanged. No old-panel containers are active.

| Design | Retired VCDs | Raw GB | Retained GB for those traces |
|---|---:|---:|---:|
| AES | 10,869 | 61.76 | 0.99 |
| DMA | 10,843 | 14.72 | 1.03 |
| Mesh | 11,427 | 556.35 | 11.84 |
| RedMulE | 8,942 | 6,381.10 | 137.39 |

GB here is decimal. Ibex produced no VCDs in this panel; its simulator logs and
other compact evidence remain preserved, including its verified 8.91 GB archive.
The old panel now occupies approximately 383 GiB locally, plus 12 GiB for the
archive directory. This intentionally retains compressed waveforms, compact
records and build collateral; it is not a blanket deletion of historical data.
Other experiments and other users' data were not targeted.

The audit also verifies all five fresh full-panel manifests and confirms that
none has a started cell or evaluation cache. No API calls were made in this
slice. The implementation passes 763 tests and repository lint checks.
