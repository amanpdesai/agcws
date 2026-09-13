# Fixed-work AES/DMA target qualification v2

This version responds to v1's necessary non-flatness failures without changing
measurement contracts, calibration, tolerance or admission margins. It applies
only to AES/DMA. Preserve all v1 requests and failures; no v1 witness panel was
launched for these designs because their banks already failed necessary gates.

Keep eight families plus the separate flat control. Match each requested vector
to the calibrated median mean. Use the largest centered shape amplitude that
stays inside the calibrated endpoints, multiplied by 0.90 for development and
1.00 for confirmation (v1 used 0.75 and 0.90). Endpoints are calibration quantiles,
not proven reachable limits. This strengthens contrast; it does not establish
feasibility. A necessary floor failure still blocks admission.

Confirmation uses v1's shape templates. Development changes dwell and phase,
not just amplitude:

| Family | Development template |
|---|---|
| activation | 0,0,0,1,1,1,1,1 |
| deactivation | 1,1,1,0,0,0,0,0 |
| burst | 0,0,1,1,0,0,0,0 |
| quiet interval | 1,1,0,0,0,1,1,1 |
| alternating | 1,0,1,0,1,0,1,0 |
| ramp | 0,.14,.29,.43,.57,.71,.86,1 |
| rise/fall | 0,.5,1,1,.5,0,0,0 |
| irregular | 1,0,.5,0,1,0,.5,0 |

These analytic choices precede new witness searches and use no policy outcomes.
Controls remain the same calibrated mean across splits, explicitly not held-out
non-flat evidence. Record pairwise distances; different names alone do not prove
independent difficulty or non-overlapping tolerance regions.

Freeze vectors before executing phase-random and phase-GA, 256 proposals each
per request, two-slot batches, no early stopping. Seeds 7800 development and
7900 confirmation. Eighteen concurrent cells per split. Retain every invalid
attempt and miss. Select the lowest measured error, ties by policy then proposal
index. Admission remains measured error <=0.10, non-flat constant-vector floor
>0.12; control target and witness floors <=0.10. No target substitution or extra
attempts within this version. These are CPU witness searches, not paid studies.
