# Bounded-context runtime replay

The policy-context change alters the global source fingerprint. It does not
authorize relabeling old measurements. AES, DMA and mesh each replayed all
64 calibration slots plus 18 selected witnesses; exact audits passed and
`results/<design>/qualified-bank-v4.json` records the current fingerprint.
Each replay archive retains its parent audit, expected records, lineage,
freeze and original bank as compressed sidecars.

Ibex separately replayed its 64 calibration slots (including full decoded
waveform comparison excluding only creation date) and 18 selected witnesses.
Admission passed in `results/ibex/qualified-bank-v4.json`. Parent frozen
configuration sidecars accompany its calibration and admission archives.

Archive pack/restore byte checks covered 734 AES, 652 DMA, 742 mesh, 957 Ibex
calibration and 272 Ibex admission files. This proves runtime compatibility
for the measured corpora, not universal equivalence or full-study readiness.

RedMulE's 64 calibration slots matched integer per-cycle activity, window
counts, outcomes and normalization exactly. Its longer-window bank remains
failed at 2/18; the separate 18-case pulse diagnostic adds no target admissions.

Next gates: resolve RedMulE qualification without relaxing target gates;
declare and complete new bounded-context Flash feedback smokes; freeze the
full-study settings and fresh seeds. No full study has been launched.
