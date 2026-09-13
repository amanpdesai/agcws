# Five-design calibration v1

Procedure: [frozen qualification protocol](../../docs/TARGET_QUALIFICATION_V1.md),
source commit `34cec4f31`. CPU-only, 64 proposed candidates per design, no model
calls. These corpora establish calibration, not qualified benchmark targets or
policy-comparison results. Each completed design has a compact evidence archive
and `calibration.json`; the packer verifies restoration against the original files.

AES, DMA and mesh completed with 64/64 valid proposals each. RedMulE completed
with 59/64 valid proposals and five useful-work rejections, all retained. Ibex is
still in progress at this archive update; absence is not a successful admission.

AES's whole-window mean spans only 23.3355–23.3607 transitions per edge, while
per-bin values span 2–172.8853. Its exact-work constraint materially restricts
the requested mean. Mean matching is necessary but does not ensure sufficiently
non-flat requests: activation and quiet-interval floors are 0.09829 on development
and 0.11794 on confirmation, below the declared >0.12 gate. Those four requests
fail a necessary admission condition before any witness result. They must not be
advertised as qualified or silently adjusted. Mesh's analytic requests clear this
necessary floor check; their feasibility still requires measured witnesses.

Full five-design readiness remains open. No paid paper study has launched.
