# Decision log

## 2026-09-05 — Select V4 from the complete balanced development panels

**Decision.** Freeze semantic-edits-v4 with Gemini 2.5 Flash for both designs'
held-out evaluation, using the existing V3 prompt text and V4 sampling settings.
The predeclared 30-cell balanced mean AUC is 2.0595 for V4 versus 3.1320
for V5. Every candidate cell passed independent ledger audit before selection.
**Rationale.** V5 improved AES but regressed substantially on DMA. Choosing V5
only on AES would violate the common-controller comparison.
**Consequence.** Capture prompt, executable source, package, calibration and
pricing configuration before any seed 200–209 runs. Retain all development
failures and unknown usage. Held-out losses or null results must be reported;
selection does not establish superiority or equivalence.

## 2026-09-05 — Version the AES transaction oracle and recalibrate before comparison

The legacy simulator ignored DSL key length and direction and reset between
blocks. Its search results describe pacing of repeated AES-128 encryption,
not full execution of the advertised DSL. The partial semantic development
suite is retained with that limitation and stopped.

The transaction backend executes the ordered DSL with a single initial reset,
reference-checks every block, scopes activity to the DUT, and collects measured
Verilator basic-block line coverage. Twenty seed-0 workloads define the new
activity envelope 20.145905199948896–197.84064022268615; all exceed the fixed
38-block floor (minimum 47). Five seeds of 20 random proposals each were then
checked before comparisons: median target coverage r=1.0 at epsilon 0.05,
and r=0.6 at epsilon 0.02 after the permitted adjustment. Epsilon 0.02 is used
for this oracle version; the strict r>0.6 triviality condition is not met.
The 100 reference-checked workloads and provenance are archived under
results/aes_transactions_calibration. This new oracle cannot share bounds or
comparative tables with legacy results.

## 2026-09-04 — Refresh AES activity calibration after generator widening

**Decision.** Replace the pre-widening 10-sample envelope (128.724--130.434)
with the 20-sample widened-generator corpus (14.374--130.208 transitions per
clock edge). All 20 workloads passed the useful-work gate; the minimum useful
work was 47 blocks, above the floor of 38. The refreshed corpus covered four of
five declared scalar targets at epsilon 0.05 (r=0.8), triggering the one
permitted recheck. At epsilon 0.02 it covers one of five (r=0.2), so epsilon
0.02 is now frozen.
**Rationale.** The old artifact was frozen before the workload generator was
widened and normalized the Vertex study onto a 1.3% slice of the documented
activity envelope. The calibration must describe the generator used by the
comparative study.
**Rejected.** Reusing the old artifact; hand-editing bounds from the narrative;
re-tuning epsilon per design or after comparative results.
**Consequence.** The checked-in calibration is now the required source for the
AES Vertex matrix, and the runner rejects narrow envelopes before making calls.

The old r=0.2 value was measured against the obsolete narrow corpus; it is
historical context only. The finalized r=0.2 is the epsilon-0.02 recheck on
the widened corpus.

## 2026-08-31 — Ibex Verilator warnings remain visible but non-fatal

**Decision.** The shared Ibex RTL checker passes `-Wno-fatal` while retaining
Verilator diagnostics in the command output.
**Rationale.** The pinned closure produces version-dependent duplicate-package
and `UNOPTFLAT` warnings that do not prevent elaboration or simulation. Treating
them as fatal made host and container checks disagree without improving the
validity boundary.
**Rejected.** Suppressing the warning classes entirely, or treating a warning
pass as evidence of successful gate-level synthesis.
**Consequence.** A nonzero Verilator error still fails the check; Ibex remains
supported at the RTL simulation/activity boundary only.

## 2026-08-31 — Dependency-free paired inference for final comparisons

**Decision.** Implement exact paired sign-flip permutation p-values, Holm
adjustment, and matched-pairs rank-biserial effect sizes in
`agcws.analysis.inference`; retain deterministic bootstrap confidence intervals
for means.
**Rationale.** These procedures are required by the pre-registration, and a
small dependency-free implementation keeps analysis reproducible in the base
container while making finite-sample behavior explicit.
**Rejected.** Unrecorded notebook-only statistics or silently adding SciPy as a
runtime requirement for the core artifact.
**Consequence.** Final reports must record the pairing key, input vectors, and
deterministic procedure used for every comparison.

## 2026-08-31 — Ibex RTL closure validated with Verilator; synthesis remains separate

**Finding.** The corrected standalone Ibex closure contains 91 sources after
restoring omitted packages and include-only files. It passes Verilator lint in
the reproducible Docker image. Slang/Yosys still fails during elaboration, and
native Yosys fails on the SystemVerilog package syntax.
**Decision.** Verilator is the supported Ibex simulation/activity boundary;
Slang/Yosys is retained as an explicitly separate synthesis probe. No Ibex
gate-level power result is admitted until that probe succeeds.
**Rationale.** This preserves a valid RTL result without conflating simulator
compatibility with synthesis compatibility.
**Rejected.** Treating the Verilator pass as evidence of a mapped netlist or
silently substituting a different frontend for comparative power runs.
**Consequence.** `make check-ibex-rtl` and the container smoke enforce the
Verilator boundary; synthesis claims remain fenced and reproducible.

## 2026-08-31 — Reject incomplete Ibex source closures before synthesis

**Finding.** The upstream `ibex_top` FuseSoC `lint` target emits the generic
primitive mapping fileset but omits `files_rtl`, including `ibex_top.sv`.
Slang therefore reports no valid top-level module rather than an RTL error.
**Decision.** The source resolver now requires the manifest's declared top
module to appear in the resolved SystemVerilog closure and fails otherwise.
**Rationale.** A manifest without its top could otherwise be fingerprinted and
passed to synthesis, creating a misleading integration result.
**Rejected.** Silently accepting the incomplete closure or treating the
frontend's generic missing-top diagnostic as a design failure.
**Consequence.** The Ibex synthesis path remains open, but its current failure
is now reproducible and attributable to FuseSoC target selection; no gate-level
Ibex claim is made until the RTL fileset is restored.

The resolver now restores the direct `files_rtl` entries from `ibex_pkg.core`,
`ibex_core.core`, and `ibex_top.core`, producing an 86-source closure that
includes the package, core, and top RTL. The corrected closure reaches Slang
elaboration but still fails there; that remaining failure is tracked separately
and is not converted into a synthesis result.

On 2026-08-31, the corrected closure was tested with Slang's default mode,
`--single-unit`, `--compat all`, and both options together. All four reached
the same `Design elaboration failed` result, so compilation-unit and generic
compatibility flags are not sufficient to resolve the remaining issue.

As a negative control, the same 86-source closure was passed to Yosys
`read_verilog -sv`; it failed before hierarchy with an unresolved
`prim_ram_2p_pkg::Ram2pReqWidth` package identifier. Native Yosys is therefore
not accepted as an Ibex fallback frontend.

## 2026-08-31 — Ibex synthesis probe remains unclaimed at gate level

**Finding.** FuseSoC source closure resolution and simple-system simulation are
reproducible in the container. The original standalone `ibex_top` probe
(57 RTL sources, 33 include directories) failed during Slang/Yosys elaboration
before mapping; the later corrected closure is 86 sources and still fails at
elaboration. No Ibex netlist or OpenSTA power number is used.
**Decision.** Keep Ibex in the simulation/activity tier until the frontend
boundary is fixed and independently validated.
**Rationale.** A successful simulator run does not establish synthesizability;
publishing a proxy or partial netlist would overstate the cross-design claim.
**Rejected.** Rewriting upstream Ibex RTL or scoring a failed synthesis as a
valid power result.
**Consequence.** The next Ibex integration task is to isolate the unsupported
elaboration construct or establish a documented synthesis wrapper, followed by
netlist, annotation, and OpenSTA checks before Ibex enters gate-level claims.

## 2026-08-31 — Cross-PDK smoke requires the Slang synthesis frontend

**Decision.** The AES cross-PDK flow uses the Yosys Slang frontend for host
runs, with copied Sky130 HD and Nangate45 Liberty files. The compatibility
frontend remains available for simpler designs but is insufficient for the
current OpenTitan AES source set.
**Rationale.** A real two-PDK smoke completed with Slang and produced OpenSTA
reports for both libraries. The compatibility frontend failed on an OpenTitan
unpacked-port construct before synthesis.
**Rejected.** Rewriting third-party RTL to satisfy the compatibility frontend;
treating a failed frontend run as a valid power result.
**Consequence.** Host setup must expose `AGCWS_SLANG_PLUGIN`; Docker supplies
the plugin. The smoke records both Liberty hashes and the waveform hash. A
single waveform is a toolchain check, not rank-agreement evidence.

## 2026-08-31 — AES evaluator determinism verified

**Finding.** Two independent evaluations of the 24-block scored AES workload
produced byte-identical VCD and activity artifacts, identical useful work (24
blocks), and identical Sky130 OpenSTA mean power (`0.02118620276451`). The
machine-readable record is `out/aes-determinism-final/determinism.json`.
**Decision.** Treat the current simulator/activity/OpenSTA configuration as
deterministic for calibration and comparative runs; rerun this check after
changing simulator, frontend, synthesis, or activity code.
**Rationale.** The calibration assumes evaluator noise does not determine the
result. Hashing both waveform and extracted activity detects nondeterminism that
a matching scalar power value could hide.
**Rejected.** Checking only the final power scalar; accepting waveform
differences without measuring them.

## 2026-08-30 — Own repo, upstream CHIA as pinned read-only dependency

**Decision.** `agcws/` is standalone; `tools/chia` is pinned and read-only.  
**Pinned commit:** `d78ad77e4ce7b11523bf15a253a258c0f8795673`  
**Rationale.** Keep experiments separate from framework work and make upstream extraction reviewable.  
**Rejected.** Fork-and-branch development inside `ucb-bar/chia`.

## 2026-08-31 — Freeze AES calibration from activity-only inner-loop run

**Superseded by the 2026-08-31 container calibration refresh below.**

**Decision.** AES ε_s is frozen at 0.05 globally. The prescribed five-seed,
five-target random-search calibration solved 5/25 cells (r=0.20), which is
inside the retain-0.05 band. The activity envelope is 128.726293–130.431250
total transitions per clock edge, and the AES useful-work floor is frozen at
36 blocks from the inclusive 10th percentile of the nine valid records in the
ten-workload corpus.
**Rationale.** Calibration uses the same deterministic activity proxy as the
fast search loop; OpenSTA remains a finalist validation tier. The pre-declared
rule therefore determines ε without per-design or post-hoc tuning.
**Rejected.** OpenSTA per candidate during calibration; changing ε after
inspecting comparative results.
**Consequence.** ε_s=0.05 and the 36-block AES floor are fixed for comparative
runs. Generated calibration summaries remain ignored artifacts and can be
reproduced from the pinned repository state.

## 2026-08-30 — AES first, `axi_dma` second, Ibex third

AES has the shallowest bring-up; DMA tests protocol depth; Ibex has the longest toolchain tail.

## 2026-08-31 — Pin all declared RTL sources as HTTPS submodules

**Decision.** Add `third_party/verilog-axi` at
`516bd5dadc3365b7f9e225d2af8fe0b8d804fe53` and `third_party/ibex` at
`8b8ee086aef72e0833b7f0493d9d33f1e4d3c8e2` as HTTPS submodules.
**Rationale.** The declared three-design study must reproduce against exact RTL
revisions without vendoring third-party trees. HTTPS works in clean containers
and for reviewers without configured GitHub SSH keys.
**Rejected.** Floating branch clones; copying RTL into the project tree.
**Consequence.** Harness bring-up can proceed against immutable source inputs;
RTL updates require a new decision and refreshed measurements.

## 2026-08-30 — Local compute, credits reserved for LLM

Simulation/synthesis/STA run locally; GCP credit is reserved for Vertex AI.

## 2026-08-30 — Non-LLM search before the agent

Close the loop with hill-climbing first to establish a fair harness and fallback result.

## 2026-08-31 — OpenTitan AES as the first real design dependency

**Decision.** Use the HTTPS-pinned `third_party/opentitan` submodule at commit
`b16f2be75d2f38c62d861208453ed5b81ccf41b0`; use its TileLink-connected `aes`
top level for the production adapter.
**Rationale.** It is an established, self-contained crypto IP with meaningful
internal hierarchy and legal register/data workload semantics.
**Rejected.** Driving only `aes_cipher_core` as the headline interface; it
would simplify bring-up but would not represent a realistic legal workload.
**Consequence.** The first harness must provide deterministic TileLink,
entropy, lifecycle, key-manager, and alert plumbing.

## 2026-08-30 — Proposal-counted evaluator budgets

**Decision.** N=200 for scalar and N=300 for profile goals; every proposed candidate consumes budget, including malformed and rejected candidates. Simulations are secondary.  
**Rationale.** Prevents free LLM retries and makes validity visible.  
**Rejected.** Counting only simulated candidates; wall-clock equalization.  
**Consequence.** N remains provisional until Slice 4 runtime calibration.

## 2026-08-31 — Freeze AES scalar epsilon at 0.10

**Superseded by the 2026-08-31 container calibration refresh below; ε=0.05 is
the current authoritative value.**

**Decision.** AES ε_s is frozen at 0.10 normalized envelope units. The initial
0.05 run solved 0/25 target-seed cells within 20 proposals; the one permitted
0.10 re-evaluation also solved 0/25. No further adjustment is permitted.
**Rationale.** This follows the preregistered rule without per-design or
post-hoc difficulty fitting.
**Rejected.** Additional loosening, per-target retuning, or dropping unsolved
cells.
**Consequence.** Unsolved runs remain right-censored at the budget; ε=0.10 is
used for subsequent comparative runs, with 0.02 and 0.05 as sensitivities.

## 2026-08-31 — Superseded: freeze AES useful-work floor at 21 blocks

**Decision.** Scored AES workloads must complete at least 21 blocks, the floor
of the inclusive 10th percentile of the 10-valid-workload calibration corpus.
**Rationale.** The hard floor prevents low-power results from being idle
solutions while remaining grounded in observed workload support.
**Rejected.** A zero-work threshold or selecting the floor after comparison.

**Superseded by the activity-calibration decision above.**
**Consequence.** The 16-block workload remains a harness test, not a scored
experiment workload.

## 2026-08-30 — Pre-declared tolerance calibration

**Decision.** ε_s=0.05, ε_c=0.05, ε_t=0.10, with at most one AES-derived global scalar adjustment using the rule in `EXPERIMENTS.md`.  
**Rationale.** Avoids per-design post-hoc difficulty fitting.  
**Rejected.** Absolute-watt or per-design tolerances; dropping unsolved runs.

## 2026-08-30 — Four-stage validity gate

**Decision.** SCHEMA → PROTOCOL → FUNCTIONAL → USEFUL WORK; invalid workloads receive no score and useful-work floors are hard gates.  
**Rationale.** Prevents simulator undefined behavior and idle solutions from winning.  
**Consequence.** Floors are provisional until Slice 4 and then frozen here.

## 2026-08-30 — Generic frozen agent prompt

**Decision.** Flash for scalar, Pro for profile goals; one design-agnostic prompt frozen after Slice 6 with a recorded hash.  
**Rationale.** Preserves the cross-interface generality claim and makes prompt changes auditable.  
**Rejected.** Per-design prompt tuning and silent model substitution.

## 2026-08-31 — Sky130 HD primary Liberty; Nangate45 cross-check

**Decision.** Use the copied Sky130 HD TT Liberty as the primary validation
library and copied Nangate45 typical Liberty as an independent cross-check.
**Evidence.** Sky130 contains 2,477 `internal_power` groups, 2,477 rise-power
tables, 2,477 fall-power tables, 428 leakage entries, 1,328 capacitance entries,
and 6 clock-gating declarations. Nangate45 contains 2,459, 2,459, 2,459, 126,
404, and 8 respectively. SHA-256 digests are recorded in
`third_party/liberty/README.md`.
**Rationale.** The characterized tables support relative synthesis-level power
analysis; the second library tests whether finalist ordering is robust to
library choice.
**Rejected.** Treating RTL toggles as the final power claim or relying on host
`/opt/eda` paths.
**Consequence.** Reports distinguish per-cycle toggle activity from OpenSTA
synthesis-level power and include cross-library rank agreement.

## 2026-08-31 — Initial cross-PDK result treated as a diagnostic

**Finding.** The four-workload AES temporal corpus produced opposite mean-power
ordering under the two libraries (`Spearman rho = -1.0`). Sky130 and Nangate45
therefore cannot be treated as interchangeable absolute or ranking oracles from
this sample.
**Decision.** Preserve both results, report the disagreement, and expand the
corpus before making any cross-PDK robustness claim. Per-cycle toggle activity
remains the library-independent temporal signal; OpenSTA power remains a
library-specific validation measurement.
**Rejected.** Selecting whichever PDK agrees with the desired narrative or
silently pooling the two power scales.
**Consequence.** Cross-PDK rank agreement is a reported diagnostic and not an
assumed success criterion; the experiment must distinguish activity-profile
agreement from mapped-power agreement.

## 2026-08-31 — Cross-PDK agreement is reported by corpus class

**Finding.** The identical 10-workload AES random corpus (seed 17) produced
`Spearman rho = 1.0` between Sky130 and Nangate45 mean-power ordering, while
the four-workload temporal schedule corpus produced `rho = -1.0`.
**Decision.** Report corpus-class-specific agreement and retain both datasets.

## 2026-08-31 — Refresh AES calibration under the reproducible container

**Finding.** A fresh ten-workload corpus (seed 7) executed inside `agcws:dev`
with the pinned Verilator/Yosys/OpenSTA toolchain. Its activity envelope is
128.723790–130.434211 total transitions per clock edge, and the inclusive
10th-percentile useful-work floor is 38 blocks.
The prescribed five-seed × five-target random calibration then solved 5/25
cells (`r=0.20`) within 20 proposals at ε=0.05.
**Decision.** Supersede the earlier 128.726293–130.431250 / 36-block record
for future runs. Keep ε_s=0.05 and its already-recorded five-seed calibration
decision unchanged; this refresh changes the measurement corpus, not the
pre-registered adjustment rule.
**Rationale.** Calibration and comparative runs must use the same reproducible
container toolchain. The earlier values were generated before the container
workflow was the authoritative execution path.
**Rejected.** Mixing host-generated and container-generated envelopes or
silently retaining the older floor because it was already documented.
**Consequence.** Comparative invocations must use the refreshed envelope and
the 38-block hard useful-work floor. The generated corpus remains an ignored
artifact and is reproducible from the pinned checkout.
Do not average the coefficients or present the random-corpus result as proof
that temporal profile rankings transfer across libraries.
**Rationale.** Random workloads and hand-shaped temporal schedules probe
different operating regimes; their disagreement is scientifically meaningful.
**Consequence.** Future claims require larger, preregistered corpora and must
separate activity-shape agreement from mapped-power rank agreement.

## 2026-08-31 — Twenty-workload cross-PDK rank validation

**Finding.** The reproducible 20-workload AES corpus produced Sky130 mean-power
values from 0.0215984602–0.0215986948 W and Nangate45 values from
0.0050142030–0.0050142985 W. The workload ordering agreed with Spearman
`rho = 1.0`; deterministic bootstrap resampling produced a CI numerically
equal to 1.0.
**Decision.** Record this as expanded diagnostic evidence, while retaining the
earlier temporal-corpus disagreement. Cross-PDK agreement is corpus-dependent
and is not treated as a universal transfer claim.
**Rationale.** A larger random corpus tests rank robustness without erasing the
different behavior observed for hand-shaped temporal schedules.
**Consequence.** Reports must identify corpus class and PDK; mapped-power rank
agreement remains separate from library-independent RTL activity agreement.

## 2026-08-31 — Activity oracle is the compositional inner loop

**Decision.** Compositional search computes region shares from deterministic
RTL activity and does not invoke OpenSTA for every candidate. OpenSTA remains a
separate finalist-validation step.
**Rationale.** Region attribution is defined by the adapter's explicit RTL
signal-prefix map, while synthesis-level power is a slower scalar validation
measurement. Keeping the evaluator boundary consistent with temporal search
preserves the declared cost model and makes profile-search budgets meaningful.
**Rejected.** Running OpenSTA for every profile candidate; using an unannotated
gate-level report as a fabricated region attribution.
**Consequence.** Compositional trial provenance records `fidelity: activity`;
finalist reports must carry their separate synthesis fidelity and annotation
coverage.

## 2026-08-31 — Ibex probe uses the selected FuseSoC closure without duplicate vendor packages

**Finding.** The standalone `lowrisc:ibex:ibex_core` closure elaborates with
Slang/Yosys after removing duplicate primitive package copies; the simple-system
wrapper remains a separate frontend boundary.
**Decision.** Prefer FuseSoC-exported package sources when the manifest already
contains them, and keep generated FuseSoC work under the artifact root.
**Rationale.** Passing the same package twice causes deterministic Slang
duplicate-definition errors and obscures whether the selected closure itself is
 synthesizable.
**Rejected.** Editing pinned Ibex RTL or silently ignoring frontend errors.
**Consequence.** The core frontend boundary is now verified, while no mapped
Ibex power result is claimed until synthesis and mapping are completed.

## 2026-08-31 — Corrected coupled-DMA activity calibration bounds

**Finding.** The first random calibration was invalid as an envelope because
the generator emitted one fixed workload. A second version also exposed
out-of-bounds and overlapping descriptors in the coupled 64-KiB RAM oracle.
The corrected generator uses varied lengths and distinct in-bounds pages.
Three seeds and 48 valid proposals produced 16 distinct activity values with
bounds `19.674030658250675` to `19.80286241920591` transitions per clock edge.
**Decision.** Retain these bounds in `out/axi-dma-calibration-corrected-3seed.json`
as preliminary activity calibration only; do not present them as OpenSTA power.
**Rationale.** A responsive, valid workload space is required before a DMA
search matrix can be interpreted. Recording the generator failures prevents
the stale one-point corpus from entering the study.
**Rejected.** Reusing the fixed-workload corpus; dropping functional failures;
using placeholder `[0,1]` bounds in comparative results.
**Consequence.** The DMA matrix must be rerun with these measured bounds and
additional seeds before comparative conclusions are drawn.

## 2026-09-01 — Profile target manifests are not interchangeable

**Finding.** The temporal achieved-target manifest used by the original pilot
contained one target (`low_high_low`); the current temporal manifest used for
the policy matrix contains four. The current compositional manifest contains
three achieved targets.
The reported three-seed profile snapshot executes temporal target 0 and
compositional target 0 only.
**Decision.** Do not synthesize or duplicate a missing temporal target. Treat
target-index failures as pre-run configuration errors and report the executed
target cardinality explicitly.
**Rationale.** Profile feasibility requires achieved targets; inventing a
temporal target would violate that rule and make the G4 claim opaque.
**Rejected.** Reusing a compositional target as temporal; silently falling back
to the built-in smoke target.
**Consequence.** Target cardinality is recorded per manifest and matrix; no
profile generality claim is made from the preliminary AES activity matrices.

## 2026-09-01 — Compositional policy matrix uses the three-target manifest

**Finding.** `out/aes-compositional-targets.json` contains three achieved
region-share targets, while older pilot notes referenced five targets from a
superseded corpus.
**Decision.** Run and report only the three targets present in the pinned
manifest: 15 target-policy groups, three seeds, 32 proposal slots per run.
**Rationale.** Target cardinality must come from the machine-readable achieved
profile manifest; inventing or duplicating targets would invalidate the
feasibility construction.
**Rejected.** Reusing stale five-target notes or silently generating targets
outside the recorded corpus.
**Consequence.** The completed matrix has 1,434 valid trials out of 1,440
proposal slots and remains preliminary AES activity-oracle evidence.

## 2026-09-01 — Ibex core frontend passes; mapped synthesis remains exploratory

**Decision.** Treat the containerized `ibex_core` Slang frontend probe as
supported, but do not treat Ibex mapped-netlist power as supported until mapping
completes. Clean Sky130 and Nangate45 mapping attempts reached the mapping flow
but did not complete in their supervised runs after frontend elaboration
succeeded. The probe no longer imposes an application timeout.
**Rationale.** This separates a verified frontend capability from an unverified
power pipeline and preserves an honest reproducibility boundary.
**Rejected.** Calling the timeout a successful synthesis result; claiming Ibex
power from RTL activity alone.
**Consequence.** Ibex remains an RTL/source-closure capability in the report;
the incomplete mapping manifests are retained as diagnostic evidence.

## 2026-08-31 — Upstream coupled-DMA test is optional reference verification

**Finding.** The pinned `verilog-axi` upstream MyHDL test passes when its Icarus
VPI module is built from both checked-in MyHDL sources. The test exercises a
coupled AXI RAM model and validates read/write behavior.
**Decision.** Expose it as `make upstream-dma-reference`, running from an
isolated temporary checkout. Keep it separate from the AGCWS runtime and retain
the project-owned independent channel harness until a native coupled workload
runner is implemented.
**Rationale.** This gives a reproducible upstream protocol oracle without
making MyHDL/VPI a hidden dependency of search experiments or contaminating the
pinned submodule with generated artifacts.
**Consequence.** Passing the reference test does not close the AGCWS coupled
DMA milestone or authorize coupled-DMA power claims.
