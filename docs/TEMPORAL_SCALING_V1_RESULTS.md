# Temporal scaling v1 qualification

Completed 2026-09-09 before the machine reboot. No simulation restart was
necessary. All twelve witness proposals and 72 search slots survived and
passed the independent compact-evidence audit (739 archived files).

## What is working

- Deterministic request generation separates duration, resolution and shape;
  it never presents a request as a feasible benchmark without a witness.
- Ten of twelve witness programs pass the full measurement gate. All ten
  have normalized range at least 0.05. The first two were selected by the
  predeclared rule; the two useful-work failures were not replaced.
- The three CPU controls ran all six cells. Shared initializations, proposal
  reconstruction, parent visibility, CPU state, activity rates and error curves
  were checked. No model calls or paid generation occurred.
- The GA exercised phase insertion, deletion, reordering, mix replacement,
  release, weight and register mutations after crossover. Bootstrap and
  immigration appear explicitly in the ledger. Instruction mutation is unit
  tested by structural fuzz tests but was not separately observed in this smoke.

| Achieved target | Legacy random AUC | Phase random AUC | Phase GA AUC |
|---|---:|---:|---:|
| 0 | 1.0352 | 1.2876 | 0.8837 |
| 1 | 0.9415 | 0.8014 | 0.8916 |

This is one seed, two phase-random-derived targets and twelve slots per cell.
It is qualification, not evidence that the GA or new sampler is stronger.
Search validity is 67/72. All five rejections are useful-work failures.

## Important negative qualification finding

None of the five synthetic eight-bin/200k requests has a matching witness at
tolerance 0.1 in this twelve-proposal pool. Best errors range from 0.5674 to
0.7154. The twenty requests with longer duration or more bins are **unsupported
measurement configurations**, not evaluated failures.

Therefore the new request script is not yet a ready-made harder benchmark.
The next corpus needs measured achievable amplitude/dwell constraints and a
balanced witness-construction pool. No-witness-found is not proof of
infeasibility. Do not quietly rename an achieved waveform as the requested
ramp or burst merely because it is a legal program.

The [plan](TEMPORAL_SCALING_V1_PLAN.md) keeps fresh-seed confirmation separate,
with no changes to the selected Pro controller or original targets. Longer
windows require a versioned evaluator and equivalence/counting gates first.

## Evidence and commands

[Compact archive](../results/temporal_scaling_v1/README.md),
[complete summary](../results/temporal_scaling_v1/summary.json), and
[frozen manifest](../results/temporal_scaling_v1/manifest.json).

```bash
python -m analysis.temporal_scaling_v1 --archive results/temporal_scaling_v1
```

Verification regenerates proposals, selects the same witnesses, independently
checks CPU/reference/window evidence, and re-integrates loss curves. It does
not independently rerun waveforms. Heavy traces remain outside Git.
The full repository suite passes 537 tests with three existing Ray/fork
warnings. Active qualification and cleanup code pass lint.
