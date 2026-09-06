# Windowed gate-power validation

Completed: 16 predeclared finalists plus four achieved references; 180 native OpenSTA reports.
This is descriptive validation of selected cases, not a new policy study or a general proxy claim.

## Findings

Temporal power is measurable: AES finalist bins span 2.887–9.569 mW and DMA bins 20.155–21.769 mW.
Nearly identical full-window means hid these shapes. The gate error uses the achieved reference RMS;
DMA’s substantial common dynamic baseline makes its relative errors small, not proof of perfect shape matching.
No gate-level solved threshold was introduced. Within each of the four target/design groups, the
four finalists retain their activity-error ordering in gate error. This selected-case observation is not
a general proxy-correlation or agent-superiority test.

| Design | Reference | Policy | Activity error | Gate NRMSE | Bin min–max (mW) |
|---|---|---|---:|---:|---:|
| AES | random_300 | Random | 0.10546 | 0.33720 | 2.887–7.012 |
| AES | random_300 | Evolutionary | 0.11449 | 0.36756 | 2.887–8.361 |
| AES | random_300 | Agent | 0.11425 | 0.36564 | 2.887–7.996 |
| AES | random_300 | Hybrid | 0.12638 | 0.40433 | 2.887–8.002 |
| AES | random_301 | Random | 0.12536 | 0.38903 | 2.887–7.993 |
| AES | random_301 | Evolutionary | 0.09921 | 0.30704 | 2.887–8.247 |
| AES | random_301 | Agent | 0.11157 | 0.34621 | 2.887–9.569 |
| AES | random_301 | Hybrid | 0.07248 | 0.22536 | 2.887–7.009 |
| DMA | random_300 | Random | 0.03485 | 0.00595 | 20.155–21.046 |
| DMA | random_300 | Evolutionary | 0.05376 | 0.00915 | 20.155–21.105 |
| DMA | random_300 | Agent | 0.06413 | 0.01092 | 20.155–21.367 |
| DMA | random_300 | Hybrid | 0.09201 | 0.01562 | 20.155–21.660 |
| DMA | random_301 | Random | 0.08151 | 0.01396 | 20.155–21.312 |
| DMA | random_301 | Evolutionary | 0.04666 | 0.00802 | 20.155–21.616 |
| DMA | random_301 | Agent | 0.11040 | 0.01887 | 20.155–21.769 |
| DMA | random_301 | Hybrid | 0.01980 | 0.00346 | 20.155–21.727 |

## Checks and scope

- RTL/GLS rising-edge grids, individual timescales, total spans and exact bin durations match.
- Native boundary/state tests pass at 1 ps and 10 ps; cuts contain no waveform timestamps.
- All windows retain full-waveform annotation: AES 90,247/90,247; DMA 36,292/36,296.
- Maximum relative leaf-switching additivity discrepancy: 2.55e-08 (limit 1e-5).
- Maximum native aggregate switching discrepancy: 4.73e-05; the separate float32 precision audit explains why leaf sums are checked.
- Maximum internal-power weighted/full discrepancy: 0.000372; diagnostic only, not forced to be additive.
- Summed measurement pipeline time: 604.10 s; two workers per matrix, with reference/finalist work overlapping.
  This includes grid/hash work and 180 OpenSTA invocations, but not prior synthesis or reference GLS.
- Functional zero-delay models omit timing-induced glitches; these are not signoff estimates.

## Review artifacts

- [Protocol](WINDOWED_POWER_PROTOCOL.md)
- [All measurements and hashes](../results/windowed_power_v1/validation.json)
- [Every profile, without case selection](../paper/window_profiles.pdf)
- [Native semantics checks](../results/window_semantics_v1/verification.json)
- [Conditional equal-valid temporal diagnostic](../results/structural_valid_evaluation_diagnostic_v1.json)

The frozen activity studies are unchanged. Gate reference normalization differs from their activity scale,
so the numerical error magnitudes are not directly comparable. The validation set contains one selected
seed per policy and previously observed references, not a new inferential panel.
