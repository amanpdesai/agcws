# Results status

This file records the strongest verified results currently present in the
repository. It is not the final paper result: the declared 10-seed,
multi-design factorial study has not yet been completed.

## Verified infrastructure

- `make verify`: 175 tests passed, one skipped; Ruff clean.
- `make research-smoke`: passed.
- `make container-smoke`: passed, including FuseSoC/Ibex source preparation
  and deterministic workload compilation.
- Containerized `make verify-ibex` now passes with a generated 10,000-instruction
  floor-compliant workload: compilation, simple-system simulation, waveform/
  counter artifact creation, and three-input provenance verification all
  succeed. This closes the Ibex RTL simulation/activity artifact boundary, not
  the separate mapped-netlist/OpenSTA boundary.
- Both checked-in Liberty files contain `internal_power`, rise/fall power,
  leakage, capacitance, and clock-gating characterization.
- The AES Sky130 mapped netlist coverage check matches all 43,619 cell
  instances across 72 distinct cell types to the Liberty (`instance_coverage`
  = 1.0); reproduce with `make check-liberty-coverage`.
- AES cross-PDK corpus: the archived 10-workload corpus at
  `out/aes-pdk-rank-20260831/corpus` validates against its paired Sky130 and
  Nangate45 report roots with Spearman ρ=`0.9999999999999998` (10 shared
  workloads); see `out/aes-pdk-rank-20260831/corpus-validation.json`.
- A fresh containerized AES cross-PDK run also completes both Sky130 and
  Nangate45 synthesis/OpenSTA passes, with waveform and Liberty hashes recorded
  in `out/aes-cross-pdk/comparison.json`. Its single-workload annotation is
  sparse (0.132% Sky130, 0.136% Nangate45), so it is provenance evidence rather
  than a broad cross-PDK power claim.
- `make synthesize-ibex-core IBEX_TOP=ibex_core` also succeeds in the
  production container from a clean artifact root: FuseSoC resolves the core
  closure automatically and the pinned Slang/Yosys mapping returns code 0.
  Its manifest records source and Liberty hashes; this remains a mapped-core
  reproducibility result, not an Ibex power result.
- `make vertex-preflight` confirms the Vertex SDK is installed and the frozen
  prompt hash is available, but reports missing `AGCWS_GCP_PROJECT` and
  `AGCWS_GEMINI_MODEL`; no cloud API call was made and no Vertex comparative
  result is claimed.
- `make analyze-baseline BASELINE_DIR=out/aes-baseline-matrix-complete
  ANALYSIS_DIR=out/final-analysis` completes successfully, producing 25
  policy-target groups (125 run summaries across five policies and five scalar
  targets) and a reproducible convergence figure. This verifies the analysis
  tooling; it is not the undeclared multi-design final study.

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

A five-seed full-budget matrix is now complete across the five policies, with
200 proposal slots per policy and seed. Paired inference is recorded at
`out/axi-dma-inference-5seed.json`; the panel remains small and underpowered for
definitive policy claims, and the result is still limited to the AXI DMA
activity oracle rather than the full multi-design study.

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
`out/aes-temporal-pilot-aggregate.json` and
`out/aes-compositional-pilot-aggregate.json`. The aggregation command recovers
target identity from archived `target.json` files, preserving four temporal
target groups and five compositional target groups with three-run denominators
and deterministic bootstrap summaries.

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
now covers targets 0 and 1. Target 1 has aggregate
`out/aes-compositional-target1-3seed-aggregate.json` with 96/96 valid
simulations and 0/3 solves. The compositional target set still has additional
unrun achieved targets.

Those remaining compositional targets are now covered as a pilot: targets 2,
3, and 4 each ran for three seeds at 32 proposals, adding 288 valid
simulations. Together with targets 0 and 1, the pilot covers all five achieved
compositional targets, 480/480 valid simulations, and 0/15 seed-target runs
solved. Per-target aggregates are stored as
`out/aes-compositional-target{0..4}-3seed-aggregate.json` (with target 0 and 1
using their corresponding held-out aggregate paths). The repeated AUC values
across targets indicate the current random policy is not separating these
nearby region-share goals at this budget; they are not evidence of target
generality.

The remaining achieved temporal schedules are now covered as well: `high_low_high`
and `ramp` each ran for three seeds at 32 proposals, with 96/96 valid
simulations and 0/3 solves for each. Their aggregates are
`out/aes-temporal-target2-3seed-aggregate.json` and
`out/aes-temporal-target3-3seed-aggregate.json`. The temporal pilot therefore
covers all four achieved schedules, 384 valid simulations total, and 2/12
seed-target solves across the two schedules already reported plus these two.

The profile-policy seam was then exercised on two achieved temporal targets:
`out/aes-temporal-policy-matrix-20260901-v2-aggregate.json` contains five
distinct policies, three seeds per target-policy cell, and 32 proposal slots per
run. The matrix has 10 target-policy groups and 953 valid trials out of 960
proposal slots; it is a preliminary two-target activity comparison, not the
full preregistered profile factorial or a gate-level power result.
The corresponding convergence figures are
`out/figures/temporal-policy-convergence.png` and
`out/figures/compositional-policy-convergence.png`.

The corresponding compositional comparison is archived at
`out/aes-compositional-policy-matrix-20260901-v2-aggregate.json`: two achieved
region-share targets, five policies, three seeds, and 32 proposal slots per
run. It contains 10 target-policy groups and 956 valid trials out of 960
proposal slots. This is preliminary activity-oracle evidence, not a full
multi-design or gate-level result.

The five-seed full-budget aggregate is
`out/axi-dma-matrix-calibrated-200-5seed-aggregate.json`, with paired inference
at `out/axi-dma-inference-5seed.json`: 5 policies × 200 proposals × 5 seeds.
This panel is still small and underpowered for definitive policy claims; use the
machine-readable inference for exact paired statistics.
The corresponding multi-root convergence figure is
`out/axi-dma-analysis-5seed/convergence.png`, generated from the five seed
roots with `analysis/plot_search_curves.py`.

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

- Ibex core elaboration, RTL/source closure, and standalone-core mapping are
  reproducible; simple-system wrapper mapping and Ibex gate-level power
  integration remain unsupported.
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
