# Arithmetic-feedback runtime compatibility

Current runtime banks: `results/{aes,dma,mesh,ibex,redmule}/qualified-bank-v5.json`.
All preserve the prior requested vectors, scale and qualification gates.

AES, DMA, mesh and RedMulE each replayed 64 calibration slots and 18 selected
witnesses. Exact validity/rates/profile audits passed. RedMulE's six original
calibration rejections remain rejections. Ibex separately replayed its 64
calibration slots (including three rejections) and 18 witnesses, with complete
decoded-waveform comparison excluding only the creation-date header.

Verified archive restoration covered 734 AES, 652 DMA, 742 mesh, 724 RedMulE,
957 Ibex calibration and 272 Ibex admission files. Parent frozen-input sidecars
are retained alongside each archive. This is measured compatibility evidence,
not a new performance result or a universal equivalence proof.

Current payload/schema/parser reconstruction matches all 126 archived v4 calls
for each of mesh, Ibex and RedMulE. AES and DMA payloads change by design through
explicit arithmetic feedback. See each design's `context-replay-v5.json`.
Old v4 errors, unknown-cost reserves and strict failures remain unchanged.

No v5 model call or full study has launched. Next: declare an AES/DMA feedback
follow-up and resolve approval of an operational-readiness rule that preserves
metered server failures rather than requiring a zero-error sample.
