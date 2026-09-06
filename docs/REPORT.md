# AGCWS report scaffold

This is a writing outline, not the submitted four-page paper. The demonstrated
task is goal-conditioned activity-profile synthesis with matched gate-level
validation, not established arbitrary power-profile synthesis.

## Evidence to use

| Study | Scope | Authoritative report |
|---|---|---|
| Scalar | AES/DMA, five targets, ten seeds, 550 cells / 27,500 slots | [SEMANTIC_RESULTS.md](SEMANTIC_RESULTS.md) |
| Structural temporal | AES/DMA, two observed reference profiles, ten fresh seeds, 160 cells / 5120 slots | [STRUCTURAL_RESULTS.md](STRUCTURAL_RESULTS.md) |
| Gate validation | Sixteen predeclared temporal finalists, matched configuration, stimulus and waveform windows | [Finalist archive](../results/structural_temporal_finalist_validation_v1/validation.json) |

Historical pilots in RESULTS.md are not pooled with these studies. The original
three-design factorial plan is not complete; do not describe these two-design
results as that full experiment.

## Problem and contribution

Ask whether an agent can synthesize legal workloads toward requested activity
behavior across instruction, transaction and descriptor interfaces. Distinguish
the research aim (power characterization) from the measured endpoint (activity).
Do not claim automatic power-virus generation or directed switching is new.
Use the verification constraints in LITERATURE.md before citing prior work.

The reusable contribution is the typed workload interface, four-stage hard
validity gate, proposal-counted search harness, cost/provenance accounting and
matched functional gate-validation path. More expressive schedules are
implemented, but their existence does not demonstrate an agent advantage.

## Method

Describe the development/held-out separation and frozen, common controller.
For the temporal study, report exact work and observation horizons, bounded
sequence/repeat/pacing grammar, shared structural-edit operators, fixed-scale
NRMSE and 32 charged proposal slots. Record malformed/missing slots, unknown
usage and shared initialization rather than treating them as free retries.

The diversity-preserving population was an AlphaEvolve-inspired development
ablation. Its aggregate did not beat the best-eight family, so it was not
selected. It is not a reproduction of AlphaEvolve or generator-code evolution.

Use the study-specific protocols and freeze artifacts rather than substituting
the original project-wide model, budget or target settings. Both temporal
reference profiles were observed during development; fresh seeds do not imply
generalization to unseen target profiles.

## Results narrative

Lead with predeclared best-so-far AUC and paired inference, then solve rates,
censoring, validity and cost.

In the scalar study, no cross-design agent superiority or equivalence to random
is established. The temporal study also favors random in mean AUC on both
designs; AES agent-only is significantly worse than random (Holm p = 0.03125).
No agent/hybrid superiority is supported. Do not turn nonsignificance into
parity or claim random is optimal.

The temporal study has 16/16 reference-checked, matched-window GLS finalists:
90,247/90,247 annotated pins on unmasked AES and 36,292/36,296 on DMA.
Full-window mean dynamic power is not temporal target error. Nearly identical
means at matched work and duration do not validate or invalidate the eight-bin
power shape; that measurement has not been performed.

## Limitations and next experiments

Report the superseded RTL-to-netlist annotation and configuration/window
mismatches as methodological pitfalls, not current proxy-correlation results.
There is no trustworthy general proxy-to-power correlation claim here.
Functional zero-delay GLS omits timing-induced glitches and is not signoff.

The structural controller edits bounded schedules rather than arbitrary
generator programs. DMA uses fixed-size copies with pacing/concurrency, not
its full transfer-size/backpressure space. These experiments do not identify
hardware size as the cause of method ordering. A richer DMA protocol task,
generator-program evolution or another design needs fresh development and
held-out evaluation, not tuning against this observed panel.

The current experiments ran on the host. The updated validation container
smoke failed before Python execution; do not claim a verified image replay.
The final paper and upstream contribution remain separate deliverables.

## Artifact and writing checklist

- Use the tracked ledgers, manifests, inference and gate reports linked above.
- Reproduce report rendering and audits using results/README.md.
- Preserve reported scope, effect direction, censoring and unknown usage.
- If adding figures, derive them from the same complete frozen archives.
- Resolve remaining citation checks before submission.
- Keep historical Ibex, memory-backend and pilot results separately labeled.
