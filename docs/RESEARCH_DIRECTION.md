# Research assessment — 2026-09-06

This is a post-results assessment, not a replacement for either frozen protocol.
No new study or revised headline is authorized by this note.

## What the proposal asked, and what was measured

The scope asks whether an agent can synthesize legal workloads toward requested
dynamic-power behavior across heterogeneous interfaces. That contains several
distinct claims; they should not be accepted or rejected as a bundle.

| Claim | Evidence today | Boundary |
|---|---|---|
| A feedback-driven agent can generate useful legal workloads | Supported on AES/DMA, including model-origin temporal finalists | Not autonomous discovery of arbitrary low-level protocols |
| Workloads can create distinct temporal gate-power shapes | Supported by the matched eight-window measurements | Zero-delay functional GLS; selected cases, not signoff |
| Agent search outperforms strong sampling/search baselines | No general support; temporal AES agent loses to random under corrected inference | Scalar agent wins against two weaker DMA baselines, not random |
| Agents produce more expressive stimuli than other policies | Not established | Common language capacity is not comparative target coverage |
| The loop hits arbitrary power-profile requests | Not established | Search used activity; two previously observed temporal targets per design; no gate solve threshold |
| Three-design/compositional generality and fully portable artifact | Incomplete | Frozen studies cover AES/DMA; two current-image gate/window replays now pass, not full fresh synthesis |

See `SCOPE.md`, `SEMANTIC_RESULTS.md`, `STRUCTURAL_RESULTS.md`, and
`WINDOWED_POWER_RESULTS.md`. The newer gate measurement strengthens feasibility;
it does not retroactively change the search oracle or the policy comparison.

## Why the implemented test is narrower than the motivating hypothesis

1. **Low-level prerequisites are largely supplied by adapters.** The AES
   temporal lowering fixes AES-128, key/data pattern, and encryption direction;
   the controller mostly schedules work and waits. DMA lowers fixed-size copies
   and generates low-level transactions. This is useful scheduling, but not a
   direct test of discovering long hardware-specific prerequisite sequences.
2. **The two temporal references come from the random generator itself.**
   `verify_structural_aes.py` and `verify_structural_dma.py` construct
   `random_300` and `random_301` using `random_schedule`. The frozen panel uses
   those profiles. Thus it tests targets drawn from the baseline sampler's
   own distribution, not a broad independent set of requested shapes. This
   may help explain random's strength; its causal effect has not been measured.
3. **Eight aggregate bins leave a bounded scheduling task.** Fixed work,
   fixed duration and a small target panel limit the tested difficulty. They
   do not mathematically prove easy optimization or explain the method ranking.
4. **The language and the sampler are not the same thing.** The common grammar
   permits up to 128 expanded operations. `random_schedule` samples at most
   sixteen work groups and sixteen wait groups, with no explicit repeat nodes.
   Structural edits have different reachability and sampling biases. Therefore
   identical DSLs do not mean identical output distributions; more syntax or
   longer schedules would still not establish more useful target coverage.
5. **Compliance and resource bounds matter, but do not explain everything.**
   The temporal agent has seven feedback rounds after shared initialization,
   not one shot. At sixteen valid evaluations, the conditional diagnostic
   still favors random descriptively. Stronger models, more rounds and perfect
   compliance were not experimentally isolated, so none is a proven remedy.

Fairness did not inherently make semantic advantage impossible. It prevented
giving one policy a privileged API. Our particular abstraction may have removed
some of the difficulty that motivated the hypothesis. Those are different
statements. Nor does a SCHEMA failure prove hardware reasoning succeeded:
that stage includes invalid typed edits, and downstream checks were not reached.

## A legitimate extension, if we choose to pursue it

A defensible new hypothesis is: **under a fixed resource budget, semantic search
improves the fraction of feasible temporal targets reached as prerequisite or
schedule complexity increases.** This concerns effective target coverage, not
a strictly more expressive programming language.

Before running a new comparison:

- Define a small complexity ladder and what makes each level harder. Prefer
  exposing meaningful state/concurrency/transaction dependencies on the current
  designs over adding a larger DUT without an identified bottleneck.
- Define achieved target families independently of a single competing sampler;
  separate held-out targets as well as seeds. Record feasibility witnesses and
  remove them from search history. Disclose how each family was constructed.
- Give all policies the same richer representation and legality checks, without
  semantic repair reserved for one method. Include broad random sampling,
  appropriate structure-aware/coverage-guided search, and the agent/hybrid.
- Predeclare target-error tolerance, useful-work/window constraints, budgets,
  coverage and AUC endpoints, and a method-by-complexity comparison. Validate
  power shapes with matched gate windows. Do not reward complexity for its own
  sake or label larger JSON as better hardware stimulus.
- Select controllers on development data only. Use fresh frozen evaluation
  targets/seeds, report the earlier negative studies alongside the new result,
  and retain failures and censoring.

Changing a hypothesis after learning from negative results is normal research.
Presenting that new hypothesis as predeclared, reusing an observed test panel
for tuning, or omitting the original negative results is not defensible.
This extension can still lose. It is not a plan to guarantee an agent win.

## What would count as proof of better temporal coverage

The useful claim is not that an agent can emit a complicated schedule. It is
that it reaches more feasible requested shapes, or reaches them with lower
error or fewer proposals, than the same-budget baselines on unseen targets.
Measure this over an independently frozen target family, with paired seeds
and uncertainty. Include target families that differ in ordering, transitions,
concurrency and prerequisites, not just total work or overall amplitude.

Gate-window validation establishes that a waveform really changed power;
the randomized policy comparison establishes who found the better waveform.
Neither substitutes for the other. Likewise, a full-window mean loses temporal
information, but fixed useful work and duration do not guarantee identical
energy for arbitrary data patterns and workloads. Our near-invariant means
are an empirical result of this constrained panel, not a universal law.

## Recommended order

Finish safe artifact retention and a genuinely current-image replay first;
the existing evidence should survive a fresh checkout. Review the four-page
draft against the actual proposal. Then decide explicitly between shipping the
bounded result and funding one new complexity-controlled development pilot.
Do not quietly turn a new pilot into a confirmatory result or start a broad
model/design sweep while portability and submission tasks remain unfinished.

## AgentDSE-inspired follow-up — 2026-09-07

[AgentDSE](https://arxiv.org/pdf/2606.21836), §II, uses a persistent file
workspace for candidates, evaluation feedback and notes. Its single-layer
semantic ablation (§IV-B) reports 29 versus 71 simulator calls with meaningful
versus anonymized context at similar objective quality. The DOSA efficiency
comparison includes amortized offline data costs (§IV-A). These are reported
DSE findings, not evidence about temporal stimulus synthesis.

**Our proposed adaptation, not a claim from that paper:** test controller
freedom and semantic information separately before adding a larger design.
Keep the current bounded-edit controller as a reference. A workspace-based
controller could write complete schedules or small deterministic generators,
retain short testable hypotheses, and run local analysis tools. The same final
workload grammar, evaluator and resource limits remain available to all methods.
Evaluator, RTL, gate models and reference answers remain read-only; the budget
ledger is enforced outside the agent's writable workspace.

A development-only factorial could compare bounded edits versus workspace
control, each with semantic versus consistently anonymized context. Keep model,
sampling settings, budget and targets fixed, plus a random baseline. Renaming
must preserve an isomorphic legal problem and cover descriptions, schema,
feedback and accessible files; otherwise the blinded arm leaks the answer or
becomes a different task. Record local drafting/repair, token and tool costs,
and predeclare precisely when a proposal consumes budget. Every submitted
invalid candidate still costs a slot; no unmetered simulator side channel.

This would help distinguish information limitations from controller limitations.
It would not by itself prove greater temporal coverage, long-protocol reasoning,
or agent superiority. Those still require fresh target families and held-out
evaluation. No such pilot has been launched, and neither frozen study changes.

## 2026-09-07 — Programmable CPU extension completed

A separate [Ibex full-program development pilot](IBEX_EXPRESSIVENESS_RESULTS.md)
is now complete: 36 cells and 576 slots. This is not the workspace/anonymized
factorial proposed above. The CPU interface admits distinct temporal activity
profiles, but the agent does not beat broad random sampling. Exact work-count
violations dominate agent failures, so a common work-allocation representation
is the next development question before any confirmatory scaling. The earlier
AES/DMA studies and their claims remain unchanged.
