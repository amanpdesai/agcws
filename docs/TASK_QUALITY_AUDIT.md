# Five-design task-quality audit

2026-09-14. CPU-only audit; no provider calls or full comparative runs.
Operational readiness is not certification of scientific task quality.
Existing banks, thresholds and previous results remain unchanged.

## Activity and power

At fixed voltage, switching power is proportional to capacitance-weighted
transition rates: `P_switch = V²/2 × sum(C_i r_i)` when rates count both edges.
Internal power also depends on pin activity, weighted by characterized energy,
state conditions, slew and load. This is implemented directly in
[OpenSTA Power.cc](https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/power/Power.cc).
An unweighted aggregate discards which pins switched; it is not generally a
constant multiple of dynamic power, even on one fixed netlist.

Activity-directed workload generation is a legitimate research task and a
physically motivated way to probe dynamic power. Matching aggregate activity
does not itself demonstrate matching gate-power profiles. Keep the search
endpoint and gate-power validation distinct; do not discard existing activity
results merely because a power correspondence remains unmeasured.

## Measurement-contract findings

The frozen general VCD parser counts changed identifier values, not bit flips.
AES, DMA, mesh and RedMulE use this parser. Ibex uses a separate bit-transition
counter. The distinction matters even for activity-only claims.

`tests/test_activity_metric_audit.py` demonstrates with equivalent waveforms:

- One 32-bit bus flipping all bits counts as one event; 32 scalar declarations
  of the same changing bits count as 32 events, with identical clock edges.
- `b0` to `b00` counts as an event despite equal numeric value.
- A known-to-unknown transition counts rather than rejecting the waveform.

These are synthetic contract counterexamples, not evidence that padding or
unknown transitions actually occurred in the benchmark traces. Quantifying
effects on measured tasks requires trace-level checks. Tests intentionally
characterize the frozen implementation; they do not endorse it or modify it.

An independent streaming recount of the current AES confirmation-burst witness
(`d960ed58eb40954a077822ee373de090ff33efe8840bd3199e65639d8e59b91a`)
reproduces its original eight identifier-event rates exactly. Its two active
bins have 76.7379 and 97.9858 events/edge, versus 1120.9079 and 1441.9303 known
bit flips/edge. Idle bins remain 2 under either count because the scoped clock
is included. There were zero unknown-value changes and zero pre-first-edge
changes in this trace. Both metrics retain the burst shape; this example does
not show task collapse, nor does it establish equivalence across the bank.
Waveform SHA256: `1d2d311ddbeab30c4340fad2ab917403e96b1027f3d7bc705635c1dfb5081adc`.
Recount command:

```bash
.venv/bin/python analysis/activity_recount.py \
  out/aes-runtime-replay-v5/replay/cache/d960ed58eb40954a077822ee373de090ff33efe8840bd3199e65639d8e59b91a/attempt-001/activity.vcd \
  --scope aes_core_smoke.dut --clock aes_core_smoke.clk_i
```

The preselected burst/control recount now covers AES, DMA, mesh and RedMulE.
All eight traces reproduce the original identifier-event rates exactly. AES
and RedMulE retain obvious burst versus flat shapes with known-bit counting.
Mesh's flat-control witness changes from event rates 48.75–62.26 to bit rates
149.01–383.56; its apparent flatness is metric-sensitive. This does not license
applying the old event-unit calibration or tolerance to the new bit rates.
DMA has forty unknown-involving changes per sampled trace, all in bin zero,
including descriptor/response initialization at first use after reset. These
may be inactive-bus don't-cares, not illegal transfers; a validity-aware signal
mask would need an explicit contract rather than silently treating them as
physical bit transitions. No sampled other-design trace has such changes.

Evidence and offline reconstruction instructions are in
[results/task_quality_v1](../results/task_quality_v1/README.md).

## Independent geometry and witness calculations

`analysis/task_quality_audit.py` recomputes all ninety witness errors and
constant-vector floors from v6 banks and v5 measured witness replays, checks
cache identity and validity, and reports pairwise distances and cross-solves.
It invokes neither simulation nor a model. Initial calculations agree with the
published admission metrics; passing those gates is necessary, not sufficient.
The audit also independently recomputes trial losses and AUC for both classical
arms on every target using existing smokes: AES/DMA v5 seed8503, other designs
v4 seed8502. All 180 cell AUCs reproduce. These are sixteen-slot, one-seed
engineering diagnostics, not evidence of infeasibility or policy superiority.

At tolerance 0.1, two target balls can overlap whenever normalized distance is
at most 0.2. This does not prove a legal workload occupies the intersection.
Report actual witness cross-solves separately. Development and confirmation
profiles have already been exposed during engineering; fresh search seeds do
not make them unseen tasks.

## Normalization, windows and validity

Independent inclusive-percentile interpolation reproduces all five calibration
scales. All 320 attempts are retained: 64 valid each for AES/DMA/mesh, 61 for
Ibex and 58 for RedMulE. The nine rejected attempts are USEFUL_WORK. Endpoints
are the 5th/95th percentiles of valid bin rates, **not proven physical extrema**.
The same fixed scale applies to every candidate within a design. Candidates
are not peak-normalized and errors are not clipped into [0,1].

| Design | Observation | Activity scope and validity evidence |
|---|---|---|
| AES | 6,774 rising edges, reset included; bins 846/847 edges | AES DUT, scoped clock included; 64 blocks checked against AES-ECB reference |
| DMA | 9,216 edges, reset included; 1,152/bin | DMA hierarchy, clock included; 64 read/write descriptors, completion tags, status and destination bytes checked |
| Mesh | 8,200 edges, reset included; 1,025/bin | 2×2 mesh DUT; packet scoreboard, all requested packets drained, minimum 64 packets |
| RedMulE long | 262,144 edges; 32,768/bin | accelerator wrapper, software-driven timing; completed GEMMs checked against reference, minimum 1,024 MACs |
| Ibex | 200,000 marker-bounded cycles; 25,000/bin | core excluding clock and CSR hierarchy; architectural interpreter comparison, 4,096 DSL operations, retirement/phase checks and body completion before deadline |

For the four schedule backends, the enforced edge count and per-cycle-array
length are checked before scoring. Bins use slices `floor(k*N/8)`; the generic
parser's separate `window_toggles` output is not used by this path. Ibex uses
its own fixed marker window, checks period and unknown states, and excludes
reset. Thus raw rates or physical time horizons must not be pooled across
designs. A marker/clock tick is not automatically a physical power frequency.

The checks establish the declared synthetic useful work, not application-level
utility. They do not prove every internal RTL state is legal. In particular,
two-state simulation cannot demonstrate absence of four-state X behavior;
the [Verilator language guide](https://verilator.org/guide/latest/languages.html)
documents its simulation semantics. DMA's functional handshakes can be valid
while unused buses remain unknown. The audit does not relabel its forty sampled
initialization changes as protocol failures.

Eight bins deliberately cannot resolve where activity occurs inside a bin.
At normalized RMS tolerance 0.1, an error concentrated in one bin can reach
`sqrt(8)*0.1 = 0.28284` of the scale and still pass. Nonflat floors above 0.12
exclude a perfectly constant solution under the current metric, but do not
guarantee fine waveform fidelity. Preserve raw vectors, not only solve flags.
All eighty selected nonflat witnesses also exceed 0.1 constant-vector floor
under their own declared metric (minimum: AES 0.1313, DMA 0.2380, mesh 0.1797,
Ibex 0.2086, RedMulE 0.2114). Thus the current selected witnesses are not merely
flat-control-quality outputs, despite the weaker theoretical gate margin.

## Diversity and observed difficulty

Confirmation tolerance-ball overlap counts are AES 7 pairs, DMA 1, and zero
for mesh/Ibex/RedMulE. AES activation/ramp distance is about 0.1075; different
names do not constitute independent difficulty. Actual witness cross-solves
are listed separately in the scorecards. All ten controls across split
labels are handled separately from nonflat inference; AES and DMA controls
are duplicated across splits by construction.

The current confirmation engineering seed solves the following nonflat tasks
within sixteen proposals (eight tasks per design):

| Design | Phase-random | Phase-GA |
|---|---:|---:|
| AES | 1/8 | 0/8 |
| DMA | 0/8 | 0/8 |
| Mesh | 0/8 | 0/8 |
| Ibex | 0/8 | 0/8 |
| RedMulE | 0/8 | 0/8 |

This is evidence against universal triviality, not evidence of an agent
advantage, impossibility, or difficulty at 128 proposals. Feasibility comes
from separate measured witnesses. Shared first-batch initialization is included
in the charged budget. Unsolved trials remain right-censored at sixteen.
Seed8503 is used for AES/DMA and seed8502 for the other designs; no cross-design
significance or policy ordering is inferred from this table.

## Qualification history is part of the evidence

The current bank is an engineered benchmark, not a random sample of tasks.
Later witness constructors used observed measurements; these costs and earlier
misses cannot be erased or counted as evidence of an agent's reasoning.

| Design | Retained failures | Route to current witnessed bank |
|---|---|---|
| AES | [v2](../results/aes/target-qualification-v2/README.md): 7/8 nonflat and 0/1 controls per split, 9,216 proposals total | [30-slot refinement](../results/aes/witness-refinement-v3/README.md), then exact runtime replays |
| DMA | [v2](../results/dma/target-qualification-v2/README.md): 3/8 nonflat and 0/1 controls per split | [New 9,216-cycle contract/calibration and 54 serialized proposals](../results/dma/window-v3/README.md); old bank retained |
| Mesh | [v1](../results/mesh/target-qualification-v1/README.md): development 6/8, confirmation 5/8, both controls pass | [140-slot refinement](../results/mesh/witness-refinement-v4/README.md), original targets preserved |
| Ibex | [v1](../results/ibex/target-qualification-v1/README.md): 2/8 nonflat and no control per split | [216 measured-mixture programs](../results/ibex/model-witnesses-v1/README.md), then calibration and witness replay |
| RedMulE | [short-window v1](../results/redmule/target-qualification-v1/README.md), [v2](../results/redmule/pulse-witness-v2/README.md), [v3](../results/redmule/pulse-witness-v3/README.md), [refinement](../results/redmule/witness-refinement-v4/README.md); [long-window baseline](../results/redmule/long-window-v1/README.md) admits only 1/8 and no control per split | [486 expert per-bin proposals](../results/redmule/long-bin-witness-v1/README.md), 267 valid and 219 rejected; eighteen unchanged long-window requests qualify |

The linked versioned archives preserve attempts, not just selected witnesses.
Their existing qualification audits are not new independent resimulations in
this audit. All target families remain reported, irrespective of later policy
outcomes. The expert constructors are potential stronger baselines, not proof
that an LLM uniquely possesses the required expressiveness. Shared phase/release
vocabulary is an interface/design confound, not proof of witness leakage.

## Power validation and prior-art boundary

The pinned local OpenSTA `a9a3f30` implementation explicitly computes switching
as `.5 * load_cap * volt² * activity.density()` and internal terms using Liberty
energy, duty and activity. The aggregate event metric omits these weights.
The [Intel/SNUG power methodology paper](https://verilator.org/papers/Active_Power_Primetime_PX_SNUGBos10_paper.pdf)
also motivates auditing activity mapping and distinguishing zero-delay activity
from timing-aware glitch activity. Existing
[windowed gate measurements](WINDOWED_POWER_PROTOCOL.md) validate their selected
AES/DMA finalists, not these five new banks or general power fidelity.

The [HPCA2026 dI/dt work](https://lca.ece.utexas.edu/pubs/jiang_hpca26.pdf)
uses activity-driven power modeling and PDN analysis for oscillatory stress.
Our eight-bin activity objectives are neither supply-current derivatives nor
voltage-noise measurements. Periodic shaped workload generation is prior art;
arbitrary requested vector matching under a common interface remains the
specific task. No claim of semantic understanding follows merely from winning
this task; mechanism/context ablations remain necessary for that attribution.

## Task identity versus policy identity

Current `engine.source_inventory()` hashes all `src/agcws` files, including
policy code, into measurement identity. This is conservative but overbroad.
Do not bypass its mismatch checks to reuse old results after editing an
algorithm. A future explicitly versioned identity split must preserve:

- **Task:** exact target vectors, calibration corpus and scale, tolerance,
  window/clock/scope/counting semantics, functional and useful-work gates, DSL,
  lowering, RTL configuration, tool/container identities and measurement code.
- **Comparison protocol:** requested-slot budget, batch/stop/censor rules,
  history visibility, paired seeds, and exact shared initialization programs.
  Changing the random generator can change initialization too; it is not
  automatically a policy-only edit.
- **Policy:** algorithm implementation and parameters; for models, prompt,
  schema/payload renderer, model identifier, sampling and retry settings.

Baseline-only reruns may be combined with existing model results only when
task and comparison identities are unchanged and reuse is labeled explicitly.
Changing event counting to bit counting changes the task: remeasure calibration
and witnesses, version the targets, and rerun every comparison arm. Recomputing
old model scores under a new metric does not reproduce how feedback would have
changed the model's trajectory. No identity split or runtime edit was made here.

## Frozen audit verdict and next action

**Feasibility/arithmetic: pass under v6's declared metrics. Diversity: qualified
with explicit overlap/exposure limitations. Uniform bit-activity or dynamic-power
benchmark certification: not established. Full study remains on hold.**

The snapshot in `results/task_quality_v1` fixes this assessment against exact
bank and source-input hashes. It does not promote a changed bank. The recommended
next slice is a separately versioned, common bit-transition measurement contract:
explicit clocks/scopes, width-normalized vectors, a declared unknown/masking
policy, tested boundary ownership, and fresh calibration/witness qualification.
Preserve the original event-metric results and every failed new qualification.
Recount existing traces where available; do not spend model tokens on this step.
Do not select replacement targets based on agent wins.

Alternatively, retaining v6 requires explicitly calling four designs' endpoint
identifier-event activity and acknowledging mesh's representation-sensitive
control. That is a narrower benchmark, not a physical proportionality guarantee.
The audit recommends the versioned correction before the user's full-run approval.
