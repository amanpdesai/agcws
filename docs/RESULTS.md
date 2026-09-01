# Results status

This file records the strongest verified results currently present in the
repository. It is not the final paper result: the declared 10-seed,
multi-design factorial study has not yet been completed.

## Verified infrastructure

- `make verify`: 169 tests passed, one skipped; Ruff clean.
- `make research-smoke`: passed.
- `make container-smoke`: passed, including FuseSoC/Ibex source preparation
  and deterministic workload compilation.
- Both checked-in Liberty files contain `internal_power`, rise/fall power,
  leakage, capacitance, and clock-gating characterization.
- AES cross-PDK corpus: 10 shared workloads, Spearman rank agreement about
  `1.0`; see `out/aes-pdk-rank-20260831/corpus-validation.json`.

## Preliminary AXI-DMA activity calibration

The corrected coupled-harness calibration combines three random seeds and is
stored at `out/axi-dma-calibration-corrected-3seed.json`: 48 valid proposals,
16 distinct activity values, and an observed activity range of
`19.67403066–19.80286242` total transitions per clock edge. Workloads are
non-overlapping, in-bounds, and satisfy the 4,096-byte useful-work floor.
These are activity-proxy bounds, not synthesis-level power bounds; they are
not yet used to claim a completed DMA comparative study.

A calibrated five-policy smoke matrix at 20 proposal slots is stored at
`out/axi-dma-matrix-calibrated-seed0/`, with an aggregate at
`out/axi-dma-matrix-calibrated-seed0-aggregate.json`. All 100 proposal slots
ran validly through the coupled Docker oracle; no policy reached the primary
0.05 tolerance within this short smoke budget. This is orchestration evidence,
not a comparative result.

A second seed has since completed the same matrix. The two-seed aggregate is
`out/axi-dma-matrix-calibrated-2seed-aggregate.json`: 5 policies × 20 slots ×
2 seeds, 200/200 valid simulations, and zero solves. The preregistered 200-slot
DMA comparison remains outstanding; these short runs only validate stability
of the calibrated orchestration.

The first full-budget calibrated DMA run is stored at
`out/axi-dma-matrix-calibrated-200-seed0/`, with aggregate
`out/axi-dma-matrix-calibrated-200-seed0-aggregate.json`. At 200 proposals,
random reached tolerance at evaluation 51 and offline-hybrid at 101; mutation,
evolutionary, and one-shot-agent were unsolved. All five arms completed 200
valid simulations with no validity-stage failures. This is one seed on one
activity oracle and is preliminary evidence, not a general policy ranking.

A second full-budget seed is complete. The two-seed aggregate is
`out/axi-dma-matrix-calibrated-200-2seed-aggregate.json`: 5 policies × 200
proposals × 2 seeds, or 2,000 valid coupled simulations. Random solved both
seeds; evolutionary solved one; offline-hybrid solved both; mutation and
one-shot-agent did not solve either. Seed variation is visible, so these are
descriptive preliminary observations rather than a definitive policy ranking.

Held-out profile-arm Docker smokes also complete end to end. The temporal run
(`out/aes-temporal-heldout-20260901/`) used an achieved target manifest with 8
coarse windows and produced 8/8 valid simulations with 2,444 per-cycle samples;
the compositional run (`out/aes-compositional-heldout-20260901/`) likewise
produced 8/8 valid simulations against an achieved region-share target. Neither
short smoke solved its target. These validate profile plumbing and provenance,
not the full G4 comparison.

A larger one-seed profile run is also complete. The temporal arm at 32
proposals (`out/aes-temporal-heldout-20260901-seed1/`) produced 32/32 valid
simulations, retained 2,425 per-cycle samples per candidate, and reached its
achieved target within budget. The compositional arm
(`out/aes-compositional-heldout-20260901-seed1/`) produced 32/32 valid
simulations with 672 per-cycle samples per candidate but did not reach its
target. This is a G4 plumbing/milestone result for one target and one seed,
not a comparative profile conclusion.

Machine-readable aggregates for this snapshot are
`out/aes-temporal-heldout-3seed-aggregate.json` and
`out/aes-compositional-heldout-3seed-aggregate.json`. They preserve the
three-run denominators and deterministic bootstrap summaries used by the
reporting tooling.

The profile smoke was expanded to three seeds at 32 proposals per seed. Across
the temporal arm, 96/96 simulations were valid and 2/3 seeds solved the same
held-out achieved target. Across the compositional arm, 96/96 were valid and
0/3 seeds solved its held-out region-share target. Every run retained per-cycle
activity and target provenance. This remains one target per class and is not a
general profile-method conclusion.
The original temporal manifest contained one target, but the source corpus
contains four achieved schedules. A deterministic two-target manifest is now
recorded at `out/aes-temporal-targets-2.json`; the newly executed `burst` target
covered three seeds (96/96 valid simulations), with aggregate
`out/aes-temporal-burst-3seed-aggregate.json`. The reported profile evidence
therefore spans two achieved temporal schedules, while the compositional snapshot
still executes target 0 only.

A third full-budget seed is complete. The three-seed aggregate is
`out/axi-dma-matrix-calibrated-200-3seed-aggregate.json`, with paired inference
at `out/axi-dma-matrix-calibrated-200-3seed-inference.json`: 5 policies × 200
proposals × 3 seeds, or 3,000 valid simulations. Random and offline-hybrid
solved all three seeds; evolutionary solved one; mutation and one-shot-agent
solved none. Exact paired AUC sign-flip tests give `p=0.25` for every comparison
against random and Holm-adjusted `p=1.0`; this panel remains underpowered.

## Preliminary AES scalar study

The verified AES scalar aggregate combines the original corpus with seeds 5
through 9 and is stored at `out/aes-analysis-10seed/aggregate.json`. It
contains five policies, five scalar targets, and exactly ten seeds per
policy/target cell (250 run summaries total). The corresponding convergence
figure is `out/aes-analysis-10seed/convergence.png`.

In this corpus, all policies solve the high target (`q=0.90`) at least once;
the recorded solve rates are random `1.0`, mutation `1.0`, evolutionary `1.0`,
hybrid `1.0`, and one-shot agent `0.8`. The lower targets have no recorded
solves in these runs. These are descriptive preliminary results, not a claim
that one method is superior: the corpus is AES-only, does not include the
other designs, and does not include Vertex-backed agent trials.

## Known limitations

- Ibex core elaboration and RTL/source closure are reproducible; the bounded
  Liberty-mapping probe has not completed a mapped netlist, so Ibex
  gate-level power is unsupported.
- DMA finalist OpenSTA reports have sparse activity annotation (about 1.31%
  for Sky130 and 0.77% for Nangate45 in the recorded run); they are retained
  as diagnostic evidence.
- Vertex credentials, exact model availability, and billing configuration
  are external prerequisites. No cloud-agent performance claim is made until
  `make vertex-preflight` passes and a real run records model and cost
  provenance.

The final report must replace this preliminary section only after the full
factorial run, statistical tests, finalist validation, and provenance audit
are complete.
