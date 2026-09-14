# Mesh bit-target refinement — 18/18 witnessed

The four previously missed targets now have valid witnesses within tolerance
0.10. The original 14/18 bank and all its failed attempts remain unchanged.
This supplement changes neither target vectors nor measurement, calibration,
DSL, window or useful-work gates.

| Request | Previous best error | Refined error |
|---|---:|---:|
| Confirmation alternating | 0.128385 | 0.064226 |
| Confirmation quiet interval | 0.109561 | 0.039888 |
| Confirmation rise/fall | 0.113610 | 0.025743 |
| Development activation | 0.113526 | 0.072803 |

[Frozen procedure](../../../docs/MESH_BIT_REFINEMENT_V1.md): four parallel
512-slot local searches, starting from privileged best witnesses. Every slot
is charged. No LLM calls. This is feasibility engineering, not a fair policy
comparison, and witnesses must remain hidden from comparative controllers.

- [New bank](bank.json): unchanged requests, original and refined witnesses.
- [Audit receipt](audit.json): all 2,048 proposals, parents, cache records and
  losses reconstructed, including a repeat audit after archive restoration.
- [Evidence](evidence.json.gz): path-indexed exact-text checkpoints with SHA256;
  includes every attempt, manifest, completion and cached measurement record.

Raw waveforms remain scratch. The audit reconstructs trajectories and measured
arithmetic; it does not independently resimulate all refinement waveforms.
Full Flash configurations still need refreshing and validation before launch.
