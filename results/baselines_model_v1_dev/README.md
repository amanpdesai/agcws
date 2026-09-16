# Three-arm execution and retention smoke

2026-09-16. Five designs × one alternating development target × seed 9300 ×
three CPU policies. All 15 cells finished, each at 12 charged proposals; no API
calls and no solved cells. This is **not** a comparative study or evidence of
optimizer superiority. No parameters were tuned using these results.

| Design | Random worst bin | GA worst bin | Model-guided worst bin | Valid slots, random / GA / model |
|---|---:|---:|---:|---|
| AES | 0.29014 | 0.29014 | 0.29014 | 12 / 12 / 12 |
| DMA | 0.47459 | 0.79490 | 0.69294 | 12 / 12 / 12 |
| Ibex | 0.69448 | 0.68408 | 0.69448 | 12 / 11 / 12 |
| Mesh | 0.68437 | 0.54602 | 0.51827 | 12 / 12 / 12 |
| RedMulE | 0.59252 | 0.80000 | 0.59252 | 11 / 10 / 11 |

Full curves, AUCs and identities: [summary.json](summary.json). `phase-model`
entered measured-history ridge refinement on every design (four proposals each,
two on RedMulE). The policies share the initial two proposals and evaluator.
Invalid proposals remained charged. No measurements were borrowed from the old
panel. These small observations do not establish a stronger algorithm.

Per-design manifests/configs are in `../DESIGN/baselines-model-v1-dev-plan/`.
Compact evidence is in `../DESIGN/baselines-model-v1-dev/`, with a manifest-indexed
archive verified by `maintenance/archive_study.py`: AES 290, DMA 263, Ibex 375,
mesh 290 and RedMulE 252 restored files. All restored bytes matched the runs.
The runtime implementation is commit `f20614788`; content hashes in the run
manifests are authoritative.

After completion, zero expanded VCDs remained in these five run directories.
AES/DMA/mesh each retained 26 verified compressed waveforms; RedMulE retained
20 exact FST representations. Ibex's pipeline records activity in its simulator
log and produced no VCDs in this smoke. Raw compact evidence is not deleted.

The next plan is CPU-only, three arms, 1,350 cells, 128 proposals, unchanged
every-bin ≤0.05 gate. Preparation does not authorize or launch execution. The
previously observed bank is a post-hoc robustness setting, not fresh held-out
confirmation; strict ≤0.05 feasibility remains unproven for some requests.
