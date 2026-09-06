# Structural temporal study — development plan

## Development selection completed

All 84 cells / 1344 proposal slots completed and passed independent audit in
`results/structural_population_development_v1/`. The declared balanced-family
selection chooses **best-eight**, mean AUC 2.0452708295 versus 2.0697978435 for
peak-window-population. The diversity-preserving AlphaEvolve-inspired archive
did not improve the aggregate; retain it as a tested development alternative,
not a held-out superiority claim or an implementation of AlphaEvolve itself.

Random mean AUC is 1.99215 on AES and 1.69900 on DMA. Selected edit-agent means
are 2.15797 / 2.07107; selected edit-hybrid means are 1.97098 / 1.98107. These
six-run-per-design/policy development summaries do not establish parity or a
general agent advantage. Recorded model cost is $0.3771352, with two batches of
unknown provider usage, so accounting is incomplete. No failed proposal slots
were removed or granted free retries.

Held-out integration adds phase labels and a pre-proposal frozen-manifest guard;
it does not modify either selected policy, the DSL, evaluator or target corpus.
The frozen study retains the stated tolerances, fixed scales and 32-slot budget.

## Population comparison protocol

Before running seeds 315–317, the next development panel is fixed in
`experiments/structural_population_development.json`: both designs, two achieved
reference profiles, seven policies, 16 proposal slots, batch four (84 cells).
The best-eight family is compared with a new peak-window population family.
The latter retains the lowest-loss unique schedule in each measured peak-window
niche, then fills remaining slots with lowest-loss unique schedules, up to eight.
Peak ties use the earliest window; loss ties retain history order. Duplicate
proposals still consume budget even though they do not occupy multiple archive
slots. CPU evolution, agent-only and hybrid use exactly the same selector.
All variants retain the existing typed edit API, prompt, model, random
initialization, loss and fixed-work/window contracts.

This is an AlphaEvolve-inspired diversity ablation, not a reproduction of
[AlphaEvolve](https://arxiv.org/abs/2506.13131). It does not evolve arbitrary
generator code, implement island migration, or modify any design/evaluator.
Existing CPU random-restart probability and hybrid alternation remain explicit
algorithm differences, not additional evaluator allowances.

Select one family by mean primary AUC equally weighted across design, target,
seed and agent-only/hybrid variants; ties retain best-eight. Require every
development cell before selection. Do not select a different family per design.
The completed scalar study and seed-310 pilots remain separate. Seed 311's
eight-slot CPU smoke is a mechanics check, not a panel member.

After selection, freeze source/configuration and use fresh seeds 400–409 with
32 slots for the temporal held-out comparison. Ten seeds are fixed before
evaluation; there is no optional extension based on significance.
The profiles remain previously observed reference tasks; fresh seeds test search
repeatability, not generalization to unseen target profiles. Any unseen-profile
claim needs a separately fixed target corpus before evaluation.

The DMA contract here remains fixed-size copies with pacing/concurrency. A
future transfer-length/backpressure extension is not silently mixed into this
population ablation. These restrictions bound the expressiveness claim.

Held-out seed-count amendment, before any held-out runs: the initial five-seed
plan was insufficient for the declared two-sided exact sign-flip inference
(minimum unadjusted p=2/32=0.0625). Use ten upfront, not a five-seed test followed
by significance-driven extension. Compare selected agent-only and hybrid
against random and the selected family's CPU evolutionary baseline on each
design. Average the two paired target differences within each seed, bootstrap
ten seed units with 10,000 replicates (fixed resampling seed 0), and apply exact
two-sided sign flips plus joint Holm correction over eight comparisons.
`analysis/structural_inference.py` enforces the complete 160-cell panel.
Primary endpoint remains proposal-counted AUC; unsolved runs are censored at
32. Validity, solve rate, cost and capped evaluations-to-target are secondary.
Pointwise confidence intervals and nonsignificance do not establish parity.

Finalist GLS preflight finding: the cached `out/aes-core-synthesis-final4`
netlist exposes `state_init_i[255:0]`/`state_o[255:0]` and contains `gen_masks`
logic. The current RTL transaction harness explicitly sets `SecMasking=0`,
`SecSBoxImpl=SBoxImplLut`, and `NumShares=1`. The cached netlist is therefore
not a configuration-matched validation oracle for these new workloads.
Synthesize the explicit unmasked configuration, record elaboration parameters,
and replay the same reference-checked transaction program before interpreting
any finalist power comparison. Do not reuse the legacy GLS driver's aggregated
idle count: it loses schedule ordering. Prior annotation coverage demonstrates
annotation on that older netlist, not configuration-matched power prediction
for the current transaction study. This does not alter any activity-only result.

The new matched AES smoke now passes and is archived in
`results/aes_matched_gls_smoke_v1/`. Explicit unmasked/LUT synthesis produces
the required 128-bit state interface. RTL and GLS use identical transaction
program hashes, check all 64 ciphertexts and both observe 6774 clock edges.
OpenSTA annotates 90,247 pins with zero unannotated pins on this new netlist;
internal plus switching power is approximately 0.00445728 W for this one
workload. This is validation-path evidence, not proxy rank agreement or an
agent result. The standalone `validation/` implementation has its own input
provenance and does not change the active search panel's executable sources.

The DMA matched smoke also passes, archived at
`results/dma_matched_gls_smoke_v1/`: the identical pipelined test checks 64
completed copies / 4096 bytes, identical maximum concurrency and completion
timing, and exactly 12,000 observed clock edges. GLS simulator time in its
log is 9.32 seconds for this workload; this is not a controlled cross-method
runtime benchmark. OpenSTA annotates 36,292 of 36,296 pins; four user-sideband
pins remain explicitly listed as unannotated. Both designs now have matched
validation smoke evidence, but selected held-out finalists must still be
replayed before any claim about their gate behavior.

Held-out finalist rule, declared before held-out evaluation: take seed 400 for
each of the two designs, two reference targets and four frozen policies. Select
the lowest-loss valid trial within each run, breaking ties by earliest proposal.
This gives 16 selected cases; retain an explicit missing-finalist entry if a
run has no valid trial rather than substituting another seed. Deduplicate
identical workload/configuration/window hashes for expensive GLS execution,
while keeping every case-to-replay mapping and its actual proposal source
(initialization, CPU or model). Do not choose finalists using gate scores.

Report exact useful work, window agreement, functional checks, annotation,
internal/switching/leakage components, and measured validation cost for every
selected case. This small, potentially duplicate set is descriptive validation,
not a new pooled cross-design correlation or evidence that RTL activity predicts
gate power generally. Full-window mean gate power does not validate an eight-bin
temporal power shape; that stronger claim remains outside this result.

## Four-arm DMA pilot completed

The [audited v2 DMA pilot](../results/structural_temporal_dma_four_arm_v2/pilot.json)
contains eight cells, 128 proposal slots, two reference targets and one seed.
Mean primary AUC: random 1.44988, evolutionary 1.40405, edit-agent 1.46364,
edit-hybrid 1.21443. These are development observations, not superiority tests.
All policies solve random_300 with the shared initializer at slot 3; that tie
is not evidence of an agent contribution. Only the hybrid solves random_301
(slot 5) in this pilot. Agent validity is 30/32 including initialization;
hybrid validity is 29/32 including initialization and CPU proposals.
Recorded model cost is $0.0307992, with no unknown-usage batches.

The scalar held-out panel remains frozen. Its new equal-valid-evaluation
diagnostic is explicitly post-hoc and does not authorize tuning on those seeds.
The next comparison requires a development protocol covering both designs,
then a frozen controller and fresh held-out seeds. The scope is activity-profile
synthesis. Power prediction remains unvalidated; GLS annotation coverage alone
does not license a power-targeting claim. Broad oracle work must not displace
the temporal comparison or report writing.

## DMA transfer checkpoint

The shared schedule validator now lowers to both AES and DMA. DMA work units
are 64-byte copies; a work operation groups up to eight units concurrently,
waiting for completion before the next group. Splitting work therefore changes
actual concurrency, not only a JSON field. Addresses are generated in disjoint
source/destination pages within each group, and every returned frame, tag,
status and destination copy is checked by the established pipelined harness.

DMA uses 64 work units (4096 bytes), 6000 declared idle cycles, and a fixed
12000-cycle observation horizon at 10 ns/clock. Trailing waits are retained;
completed schedules pad to the common horizon. An unfinished schedule fails
at that declared horizon and receives no activity score. This is the target's
simulation-window contract, not an arbitrary wall-clock tool timeout.

`results/structural_temporal_dma_verification.json` contains six schedules,
each repeated twice. All match the exact work/window contract. Serial grouping
observes one in-flight transfer; burst grouping observes four. Burst, paced,
low/high/low and random schedules have different eight-bin activity profiles.
Per-cycle activity and timing match between repeats; waveform hashes can differ
because of file metadata and are retained separately. The negative horizon
check is in `results/structural_temporal_dma_deadline_check.json`. The existing
seven-case unbounded-window pipelining verification still matches its prior
record exactly.

The shared entry point is `scripts/run_structural_search.py --design aes|dma`;
the prior AES entry point remains a compatibility wrapper. A DMA eight-slot
random smoke passed every exact-work/window gate. The next matched four-arm
DMA pilot will use the same v2 agent/hybrid prompt and settings, references
random_300/random_301, seed 310, 16 slots and batch 4. Its fixed normalization
scale is 40 transitions/edge (above the capability corpus peak bin rate 33.125),
with provisional tolerance 0.10. No per-candidate rescaling or per-design
controller tuning is introduced. Final tolerance/target selection remains a
separate cross-design development step before any held-out evaluation.

Typed-edit v2 is now complete at
`results/structural_temporal_four_arm_pilot_v2/`: the agent's generated-slot
validity rose from 5/24 to 20/24, without free retries. Both agent arms still
solve 0/2 targets; random has the lowest pilot mean AUC. This is an interface
improvement, not a performance win. Next transfer the same controller to DMA
before more AES tuning or a larger matrix. The observed pilot is development
data and cannot become the held-out result.

The first four-arm agent pilot is also complete at
`results/structural_temporal_four_arm_pilot_v1/`. All 128 slots and usage are
audited. Neither agent-only nor hybrid solves either target; only 5/24
agent-generated slots are valid after excluding shared initialization.
Two responses hit MAX_TOKENS; others miss exact totals. The next development
candidate will use compact typed structural operators shared with evolution,
explicit parent identities and indexed sequence descriptions. Preserve this
full-schedule v1 negative result; do not scale or relabel it as successful.

The CPU pilot is now complete and archived at
`results/structural_temporal_cpu_pilot_v1/`: 64/64 valid proposals, all with
exact work and observation duration. Random and structural evolution each
solve one of the two development targets. This confirms mechanics, not a
method advantage. Agent-only/hybrid integration and DMA transfer are next.

## CPU pilot configuration

V2 is a separately named typed-edit candidate: one structural operation per
proposal against an explicitly named parent. The parent set is the same best
eight valid trials used by structural evolution; every expanded sequence node
has an explicit index. Both use the identical swap/move/split/merge/redistribute
implementation. Unknown parents, invalid indices and illegal amounts fail and
consume slots, with the precise rejection exposed in subsequent feedback.
This is not a return to scalar-only editing: split/merge change sequence length,
and move/swap alter ordering. One operation per proposal matches the CPU arm.

V2 keeps the two references, seed 310, budget 16, batch size 4, scale, tolerance,
model and sampling unchanged. Its prompt is
`prompts/structural_temporal_edits_v2.txt`; parent count is eight rather than
the full-schedule v1 agent's four. Random/evolutionary cells are rerun under
the same captured source as the two v2 agent arms. Compare complete pilot
panels descriptively, retaining v1 failures. No final-evaluation claims or
favorable stopping rule are introduced by this development iteration.

The next agent-only/hybrid pilot retains the two CPU reference targets,
seed 310, 16 slots, batch 4, scale 200 and tolerance 0.10. Both controllers
start with the same four random candidates. Agent-only uses model proposals
thereafter; hybrid alternates model and structural-evolution batches. Full
schedules, not arbitrary patch paths, are returned. The design-agnostic prompt
is `prompts/structural_temporal_v1.txt`. Gemini 2.5 Flash uses temperature 0.7,
top-p 0.95, output cap 8192, thinking budget 512 and one proposal attempt.
Missing/invalid schedules consume slots and model usage is charged once per
batch. No reference schedule is passed to the model.

The first eight-slot agent smoke produced four valid initial random workloads
and four schema-valid model schedules that violated exact totals. Measured
work/idle totals were (64,5000), (62,5200), (62,4700), (63,4300), versus the
required (64,6000). The response ended normally, not at the output-token cap.
Its recorded estimate was $0.0063058. Exact actual/required totals now appear
in rejection feedback, available to every policy; workloads are not repaired.
This is a development diagnostic, not evidence of an agent advantage.

The initial search pilot uses the independently achieved `random_300` and
`random_301` reference profiles, proposal seed 310, 16 slots, batch size 4,
and random versus structural evolution. The reference schedules are not
passed to the policies. Evolution uses the best eight valid parents, 20%
random exploration and shared swap/move/split/merge/redistribute operators.
These operators preserve exact work/idle budgets without retrying proposals.

The new fixed-rate endpoint is `min(1, RMSE(bin rates, target rates) / 200)`;
scale 200 transitions/edge and tolerance 0.10 are provisional pilot settings,
recorded before this comparison. Capping at 1 aligns the worst valid score
with the existing invalid-prefix AUC penalty; it does not normalize by the
candidate's peak. Raw bin rates remain archived, so uncapped errors can be
inspected. The fixed horizon is 6774 edges including reset. The prior
candidate-peak-normalized temporal loss is unchanged for historical replay.

This is a two-target, one-seed development check, not the final study or
evidence that any method is superior. The first standalone random smoke
under `out/structural-temporal-cpu-pilot/` is plumbing evidence only; the
matched pilot panel is versioned separately with identical captured source.

Started 2026-09-06. This is a new research track, not a revision of the
completed scalar held-out results. No success or model advantage is assumed.

## Interface diagnosis

Replaying every archived v4 invalid patch against the original batch's four
parents reproduces the failures. AES: 473 invalid object keys, 34 invalid
parent indices, 14 invalid array indices, 24 empty/invalid paths, 4 missing
parent fields; 12 additional slots have no candidate. DMA: 210 invalid parent
indices, 197 empty/invalid paths, 15 invalid array indices, 4 invalid object
keys; 20 additional slots have no candidate. The reproducible diagnostic is
`results/semantic_patch_failure_audit.json`.

These failures were already charged in the scalar study. They are not all
malformed JSON or hardware protocol errors. The next interface should expose
complete typed schedules and explicit structural operations instead of making
the model guess mutable nested JSON paths. No free resampling or hidden repair.

## First milestone: AES capability and small comparison

Use a common bounded sequence DSL: `work(units)`, `wait(cycles)`, and
`repeat(count, body)`. Expansion is deterministic and limited in depth and
operation count. Unknown fields, invalid counts, and expansion bombs fail
before simulation. All policies receive the same grammar and contract.

The first AES contract is exactly 64 AES-128 encryption blocks, a fixed data
pattern, and exactly 6000 idle cycles. Reordering and repartitioning work/idle
changes temporal activity without changing useful work. A common adapter
lowers the schedule into the existing reference-checked transaction harness.
Do not present this restricted first milestone as general AES mode synthesis.

`results/structural_temporal_aes_verification.json` verifies compact repeat
and explicit expansion produce identical activity artifacts, and two random
structural schedules produce different eight-bin profiles. All four execute
64 correct blocks over exactly 6774 clock edges, including the same reset
window. This is representation verification, not a search result.

Next implement shared structural operators and random/evolutionary policies,
then agent-only and hybrid proposals with precise contract-error feedback.
Give all methods identical legality mechanisms. Charge every requested slot,
including rejected proposals and missing model responses. Keep candidate
failure details separate from the hardware validity stages.

## Temporal measurement and feasibility

Use eight equal-clock bins over a declared common observation window.
Compare raw bin rates with one fixed, recorded normalization scale derived
from target/calibration data. Do not normalize each candidate by its own peak;
that discards amplitude error. Keep the old temporal loss for historical
reproduction and introduce a separately versioned fixed-scale endpoint.

Construct targets from actual achieved profiles in a separate reference
corpus; archive their reference workloads but do not give those solutions to
search policies. Hold useful work and simulation duration fixed, and reject
window mismatches rather than silently clipping traces or rescaling time.
Tolerance and scale must be set on development data before final evaluation.

## DMA transfer and evaluation gates

Transfer the same schedule/controller interface to descriptor-driven DMA.
Define the work-unit lowering, mapped memory layout and legal concurrency
explicitly. Verify every transfer, useful-work total and measurement duration.
DMA completion latency can depend on schedule/backpressure, so equal requested
idle cycles alone do not establish equal observation windows. A fixed horizon
with explicit completion checks/padding must be verified on both RTL and GLS.

Run small development pilots first. Compare random, structural evolution,
agent-only and hybrid with the same proposal budget and target information.
Select one controller across both designs, not one per design. Before any
confirmatory run, record targets, source/model/prompt, loss, tolerance, budget,
seed range, selection rule and paired inference in a new freeze manifest.
The observed scalar evaluation seeds 200–209 are no longer held out; do not
reuse them for confirmatory conclusions. Capability seeds 300–301 used here
are development-only. Reserve fresh evaluation seeds after the pilot.

Validate representative finalists with direct GLS and matched waveform windows.
Report activity targeting unless gate-level evidence supports power targeting.
Archive all complete panels, invalid proposals, unknown usage and limitations.
No larger matrix or model sweep until the end-to-end pilot is mechanically sound.
