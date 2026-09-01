# Results status

This file records the strongest verified results currently present in the
repository. It is not the final paper result: the declared 10-seed,
multi-design factorial study has not yet been completed.

## Verified infrastructure

- `make verify`: 182 tests passed, one skipped; Ruff clean.
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
- The archived temporal cross-PDK diagnostic reports Spearman ρ≈`-1.0` across
  four shared schedules (`out/aes-temporal-cross-pdk.json`), indicating a rank
  inversion rather than agreement. It is excluded from validation claims until
  the temporal workload/report pairing is independently reconciled. The paired
  means are Sky130: `low_high_low=0.01852035`, `high_low_high=0.01848644`,
  `burst=0.01915642`, `ramp=0.01844827`; Nangate45:
  `low_high_low=0.00504285`, `high_low_high=0.00505190`,
  `burst=0.00499004`, `ramp=0.00506829`. The inversion is therefore a
  PDK-dependent temporal diagnostic, not evidence of cross-PDK agreement.
- A fresh containerized AES cross-PDK run also completes both Sky130 and
  Nangate45 synthesis/OpenSTA passes, with waveform and Liberty hashes recorded
  in `out/aes-cross-pdk/comparison.json`. Its single-workload annotation is
  sparse (0.132% Sky130, 0.136% Nangate45), so it is provenance evidence rather
  than a broad cross-PDK power claim.
- In the production container, the core-only Slang frontend probe succeeds
  with `IBEX_TOP=ibex_core` and 96 elaborated sources. A subsequent Sky130
  mapping attempt reaches the synthesis flow but did not complete in the
  observed run; a Nangate45 attempt likewise did not complete. The probe now
  runs without an application timeout, so these are unfinished runs rather
  than timeout-classified results. No mapped netlist or Ibex power result is
  claimed; manifests retain source and Liberty hashes for reproduction.
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

An older compositional pilot record referenced targets 2, 3, and 4 from a
superseded corpus. Those artifacts are not the current policy matrix and are
not used for its claims. The current machine-readable manifest contains three
targets, all of which are covered by the policy matrix below. The repeated AUC
values across these nearby region-share goals indicate that the current
32-proposal activity budget is not separating them; they are not evidence of
target generality.

The remaining achieved temporal schedules are now covered as well: `high_low_high`
and `ramp` each ran for three seeds at 32 proposals, with 96/96 valid
simulations and 0/3 solves for each. Their aggregates are
`out/aes-temporal-target2-3seed-aggregate.json` and
`out/aes-temporal-target3-3seed-aggregate.json`. The temporal pilot therefore
covers all four achieved schedules, 384 valid simulations total, and 2/12
seed-target solves across the two schedules already reported plus these two.

The profile-policy seam was then exercised on all four achieved temporal targets:
`out/aes-temporal-policy-matrix-20260901-v2-aggregate.json` contains five
distinct policies, three seeds per target-policy cell, and 32 proposal slots per
run. The matrix has 20 target-policy groups and 1,904 valid trials out of 1,920
proposal slots; it is a preliminary four-target activity comparison, not the
full preregistered profile factorial or a gate-level power result.
Paired policy inference for this matrix is recorded in
`out/aes-temporal-policy-inference-32.json`; each comparison has three matched
seeds per achieved target and Holm-adjusted p-values. The panel is too small for
definitive policy claims.
The corresponding convergence figures are
`out/figures/temporal-policy-convergence.png` and
`out/figures/compositional-policy-convergence.png`.

The corresponding compositional comparison is archived at
`out/aes-compositional-policy-matrix-20260901-v2-aggregate.json`: three achieved
region-share targets, five policies, three seeds, and 32 proposal slots per
run. It contains 15 target-policy groups and 1,434 valid trials out of 1,440
proposal slots. This is preliminary AES activity-oracle evidence, not a full
multi-design or gate-level result. The manifest contains three targets; older
notes referring to five targets describe a superseded corpus and are not part
of this matrix.

The rerun at the preregistered profile budget is archived at
`out/aes-compositional-policy-matrix-20260901-300-aggregate.json`: the same
three achieved region-share targets, five policies, three seeds, and 300
proposal slots per cell. It contains 15 target-policy groups and 13,410 valid
trials out of 13,500 proposal slots, with no profile-audit errors. This remains
preliminary AES activity-oracle evidence, not a multi-design or gate-level
result; the corresponding figure is
`out/figures/compositional-policy-convergence-300.png`.
Paired policy inference for this matrix is recorded in
`out/aes-compositional-policy-inference-300.json`; each comparison has three
matched seeds per achieved target and Holm-adjusted p-values. The panel is too
small for definitive policy claims.

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

## Memory-aware synthesis evidence

The memory inventory and collateral path was validated on the current pinned
RTL closures. AES `aes_cipher_core` produced zero inferred memories. AXI DMA
produced 13 internal 32-entry FIFO memories with independent read and write
ports; the pinned BSG FakeRAM backend is single-port synchronous 1RW, so Yosys
rejects that mapping and the baseline remains unchanged. Ibex core inventory
produced four memories and two unique read-only geometries (32×32 and 16×3),
but their read ports are asynchronous (`RD_CLK_ENABLE=0`), which is also
incompatible with BSG FakeRAM's synchronous interface.

BSG generation was run in an isolated checkout for the AXI and Ibex physical
geometries. CACTI-required padding is recorded explicitly as physical geometry
in the generated manifest; logical widths and depths are never silently
replaced. Generated collateral is reproducible diagnostic evidence, not a
claim that either design has been successfully macro-mapped.
