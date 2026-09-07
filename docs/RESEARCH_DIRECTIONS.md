# Research directions: separating agent capability from benchmark design

Updated 2026-09-07. This is a living roadmap, not a retroactive revision of any
frozen protocol. Individual executed stages have their own immutable protocol,
source/parameter manifest and complete evidence archive.

Stage A is now [complete](IBEX_CAPABILITY_V1_RESULTS.md): the fixed-context
model/thinking probe selects Pro-4096 for further development, with mean gain
0.14234 versus random 0.02674. It supports testing closed-loop depth next, not
claiming full-search superiority. All later stages below remain proposals.

## 1. What the project is trying to establish

The central question is whether semantic, feedback-driven workload construction
can reach requested hardware behavior more effectively than classical search,
especially when useful activity requires stateful, legal action sequences.
An agent win is a hypothesis, not a completion criterion that permits unlimited
tuning. Useful negative results should identify the controller, representation,
hardware configuration, target regime and resource budget under which they hold.

Three distinct claims must not be conflated:

1. **Search quality:** lower target-error AUC or greater solve rate at equal
   proposed-candidate budget, with separate model and compute costs.
2. **Finite-budget discovery:** reaching a broader collection of feasible profile
   families. A descriptor-grid cell count is only one operational measure.
3. **Intrinsic expressiveness:** which workloads the representation can describe.
   If every policy shares a DSL, an agent does not have a more expressive language.
   It can still discover difficult members of that language more efficiently.

Activity targeting and power targeting are also distinct. The fast CPU studies
use RTL transitions; selected AES/DMA temporal finalists have matched gate-power
validation. Neither licenses a general CPU power claim.

## 2. Evidence already available

The AES/DMA scalar and structural held-out studies do not establish broad agent
superiority. They are publishable findings about their frozen methods, not a test
of every reasoning model, agent architecture or hardware interface. Their results
and prompts must remain unchanged. See `SEMANTIC_RESULTS.md` and
`STRUCTURAL_RESULTS.md`.

The current development benchmark is **programmable Ibex, not AES**. It permits
instruction/operand dependencies and structural program changes, but uses a
restricted configuration: cache off, small memory workspace, bounded segments,
4,096 semantic operations and a 200,000-cycle observation. It does not test cache
replacement, coherence, rich memory contention or arbitrary operating software.

Ibex v3 supplied eight fixed source/specification excerpts. This was not autonomous
RTL discovery. V4 added actual operand events, retirement-phase attribution and
a prediction/outcome notebook; it did not add deeper source exploration. Both
used Gemini 2.5 Flash with 512 thinking tokens, two candidates per call and seven
feedback rounds after initialization. See `IBEX_TEMPORAL_V3_RESULTS.md` and
`IBEX_TEMPORAL_V4_RESULTS.md`.

V4's full mean AUC ordering is descriptive: random 4.831839, base 4.990451,
coverage 5.123888, grounded 5.234116. Three reused development seeds do not support
an inferential claim that the grounding package is harmful or that methods are
equivalent. An adverse mean shift is not itself proof of noise either.

All methods solve only the near-flat target. The other targets have measured
reference witnesses: **unsolved within budget does not mean infeasible**. AUC
can distinguish near-miss progress even with no solves, but sparse solves limit
what can be concluded about successful shape construction. The references must
remain inaccessible to the policy during proposal generation.

## 3. Observed failure modes versus explanations not yet isolated

| Observation | What it supports | What it does not establish |
|---|---|---|
| Base generated validity is 164/168, yet no established win | Formatting is not the whole problem | Formatting never matters |
| Direction predictions match about 38% of scorable bins | The controller's public predictions are unreliable here | General inability to reason about RTL |
| Weight edits redistribute fixed work globally | A nominally local edit can change many windows | Weighting alone causes every failure |
| Earlier execution may increase later active polling | Request times are not effective activity placement | Polling is equivalent to sleep |
| Random visits more behavior cells than agents | Current agents explore less broadly under this descriptor | Random is globally optimal |
| More diagnostic context does not lower mean AUC | This package did not improve the development mean | More context inherently harms agents |

Public hypotheses and predictions can be checked against programs and execution.
They are not access to private model reasoning. An RTL citation demonstrates
source access, not comprehension; a causal story requires an intervention and
measured evidence. Retirement gaps alone are not identified stall causes.

## 4. Unresolved experiments and their controls

| Axis | Controlled comparison | Main diagnostic | Confounds to hold fixed |
|---|---|---|---|
| Model capability | Flash versus Pro in the same model generation | Validity, next-batch improvement, prediction accuracy | Prompt, schema, history, evaluator, thought/output limits |
| Reasoning compute | 512 versus 4,096 thinking tokens | Improvement and actual billed thinking usage | Model and candidate count |
| Search depth | 16, 64, 128 proposed slots | Full AUC curves and target-family solves | Increase all baselines' budgets equally |
| Feedback cadence | Sequential proposals versus batches | Benefit from earlier observations | Same total proposals and recorded model cost |
| Source investigation | No source, fixed excerpts, bounded adaptive RTL reader | Mechanism predictions checked against trace | Same allowlist, retrieval/call budgets and no witness access |
| Controller components | Diagnostics, notebook, exploration rule separately | Individual effects and interactions | Response contract and archive/history policy |
| Representation | Complete programs versus shared reference-edit tools | Compliance, edit scope and effective phase movement | Equal legal workload space and tool access |
| Population methods | Random/evolutionary versus model-assisted generator evolution | Coverage and error per evaluation/cost | Same execution sandbox, resource and legality constraints |
| Architectural regime | Shallow to deep stateful prerequisites | Benefit versus independently specified protocol depth | Matched work/windows and witnessed feasibility |

The existing AlphaEvolve-inspired population treatment is not an evaluation of
arbitrary workload-generator program evolution or a reproduction of AlphaEvolve.
That remains distinct future work, with an untrusted-code sandbox and all nested
simulations included in accounting.

## 5. Why architectural complexity matters—and why size is insufficient

AES is a useful narrow negative case. A simple command interface can expose enough
human-designed knobs that broad sampling already covers the easy search space.
It is not a representative test of all hardware. Conversely, a much larger RTL
netlist with an equally shallow stimulus interface may buy nothing scientifically.

The intended gradient is **stateful prerequisites and interaction depth**:
operand-dependent execution, cache fill/eviction, queues and backpressure,
resource contention, arbitration, and legal setup sequences before useful work.
These are candidate mechanisms, not promises of an agent advantage. Larger designs
also increase bring-up, simulation and functional-reference cost.

Before introducing another design or configuration, specify the mechanism being
tested, give all methods a sufficiently expressive interface, and produce legal
witnesses with distinguishable profiles. Separate machine-enforced legality from
the planning difficulty: fair validation need not generate the hard action sequence
for every policy. Count per-design specification and adapter engineering honestly.
Cache-enabled CPU or richer DMA configurations are candidates, not selected tasks.
A new design/configuration requires a decision entry and a fresh protocol.

## 6. Staged order and stop/advance decisions

**A — Capability/reasoning probe, active next.** A frozen 2×2 comparison on common
observed histories, with random/coverage next-batch controls. Test generated
programs rather than judging prose. Protocol: `IBEX_CAPABILITY_V1_PROTOCOL.md`.
This isolates conditional proposal quality; it cannot measure a whole new
controller's cumulative AUC. Model availability failures are recorded, never
silently replaced with another model.

**B — Depth and cadence.** After A, make a documented controller choice and freeze
a new observed-development search panel. Log every proposal index so 16/64/128
views are prefixes of the same runs. Budget cadence separately: more observations
and more model invocations can change dollars even at equal evaluator budget.
Use target witnesses to diagnose distance to feasibility; never give the policy
the witness solution. Declare target families and tolerances before this stage.

**C — RTL/tool and architecture questions.** Choose one unresolved mechanism after
A/B, not a simultaneous model+prompt+hardware rewrite. An adaptive source reader
gets only hashed RTL/harness/specification files, never the repository root,
credentials, calibration witnesses or held-out artifacts. Test comprehension by
predicting consequences before simulation. A reference-edit tool must report actual
phase/bin placement and global allocation, not just echo the agent's intent.

**D — Confirmation.** Only after development selection, freeze the whole controller,
model/configuration and target construction. Use fresh seeds and held-out target
families with no subsequent prompt iteration. Report selection history and all
failed development stages. More development is legitimate; presenting it as an
independent confirmation would not be.

No stage automatically authorizes the next expensive panel. Each ends with a
complete archive, an honest recommendation and an explicit scope/budget decision.
The goal is identifying when semantic reasoning helps, not obtaining a positive
number by trying enough configurations.

## 7. Power validation and writing proceed separately

`WINDOWED_POWER_RESULTS.md` already reports preserved activity-error/gate-error
ordering within four selected design/target groups. An explicit stratified
correlation can summarize that observation; pooling AES and DMA errors with
different normalizations could be misleading. Sixteen selected finalists are
not a general proxy calibration corpus, and do not validate the Ibex oracle.

The window arithmetic and near-identical full-window means demonstrate why
temporal claims need temporal measurements. Equal useful work and duration do not
mathematically force equal dynamic energy for all possible hardware workloads;
the observed near-invariance belongs to those particular schedules and designs.

Keep writing the existing held-out and methodological results while development
continues. A new capability probe does not invalidate those results or require
changing their headline after observing it.

## 8. Design notes for the unimplemented stages

### Reasoning versus controller memory

Increasing the thought allowance tests resource availability within a model call;
it does not add persistent memory, another simulator observation or a better
optimizer. Record actual thought-token use, termination and output validity to
distinguish an unused allowance from a failed reasoning intervention. A different
model may use the same allowance differently. Do not infer equal cognitive effort
from equal token caps, or call the same-generation Flash/Pro probe exhaustive.

A controller-memory test should keep observations constant and vary only their
retention: best/recent history, compressed mechanism notebook, or explicit
prediction/error records. Missing history and poor use of present information are
different hypotheses. More input tokens are not a success metric.

### Depth, cadence and parallel exploration

Use one frozen maximum-budget trajectory per run and inspect predeclared prefixes.
Compare the actual error curves, not merely whether the first tolerance crossing
happens. Report the fraction of the budget spent repeating previously evaluated
programs or equivalent behavior. A cache hit still costs a proposal slot.

For cadence, distinguish one candidate per observation from independent batches
whose members share the same earlier history. Parallelism lowers elapsed time but
does not give within-batch feedback. Compare at equal proposals, while reporting
the different number of model calls, token costs and observed-data opportunities.
A population of independent explorers with an archive is a separate controller
from one long conversation; its archive selection and restart rules must be fixed.

### RTL investigation that demonstrates understanding

An autonomous reader should trace a concrete question: which state must be reached,
which operands/control signals affect latency, what enables the relevant datapath,
and which prerequisites legal software can establish. Ask for a short mechanism
prediction and source locations, then test the predicted executed events. Score
unsupported statements and contradictions as well as correct explanations.

Compare equal-budget source treatments: supplied specification alone, fixed
excerpts, and adaptive retrieval from the same hashed allowlist. Include active
configuration and harness semantics: reading an uninstantiated module or optional
cache configuration would produce confident but irrelevant reasoning. Exclude
reference solutions, result directories, secrets and unrestricted shell access.

If extra monitored signals are needed, prove that tracing/observation changes do
not change the instructions, hardware configuration or activity signal inventory.
Do not turn a changed measurement instrument into an apparent controller gain.
The agent still generates stimulus; it never edits DUT RTL or its evaluator.

### Actionable tools without giving away the solution

A useful reference-edit tool can expose allocation changes, effective segment
start/end times and bin occupancy. Distinguish static estimates from measured
execution, and avoid reporting guessed stall causes. Keep a path for complete
program construction so the helper does not reduce every method to scalar tuning.

Read-only source lookup is not a power evaluation. A submitted candidate sent to
public validation/simulation must follow an explicitly declared proposal-counting
rule; do not provide the model unlimited uncharged candidate repairs or hidden
simulations through a helper. All methods get access to the same legitimate
tools. Human-authored mechanism knowledge and constraints must be counted as
per-design engineering, not attributed to model discovery.

### More complex targets, not just more complex RTL

For a new architectural regime, predefine a gradient of prerequisites independently
of which method wins. Examples of questions include whether a requested phase
requires a particular cache state, multiple outstanding operations, a dependency
chain, or coordinated resource contention. These are proposed task mechanisms;
their feasibility and observability must be established before comparison.

Useful-work and correctness gates should reject illegal sequences but need not
construct the desired state for the policy. If an adapter performs every hard
setup sequence automatically, the experiment measures choice among prepared
knobs, not semantic planning. Conversely, deliberately withholding the interface
specification would test documentation guessing. The benchmark must expose legal
actions clearly while leaving the actual state-reaching plan to every policy.
