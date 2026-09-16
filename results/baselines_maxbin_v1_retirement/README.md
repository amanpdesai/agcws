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
