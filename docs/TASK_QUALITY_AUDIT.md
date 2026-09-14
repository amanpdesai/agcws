# Five-design task-quality audit

2026-09-14. In progress; CPU-only, no provider calls or full comparative runs.
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

## Remaining audit work

1. Recount selected real traces and quantify metric/window sensitivity.
2. Add existing-baseline difficulty and qualification-failure scorecards;
   distinguish descriptive smoke evidence from comparative inference.
3. Package reproducible inputs, scorecards, source hashes and primary-source
   measurement guidance, including limits on temporal resolution and power.
4. Specify task identity separately from policy identity for future baseline
   reuse. Do not weaken the current source fingerprint in place.
5. Record a final gate verdict and justified versioned next steps, verify,
   commit and push. No full panel starts as part of this audit.
