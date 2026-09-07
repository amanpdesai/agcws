# Ibex temporal expressiveness — development v1

Declared 2026-09-07, before comparative runs. This is exploratory development,
not an amendment to the frozen AES/DMA studies or a new superiority claim.

## Question and design choice

Does semantic, feedback-driven program construction improve finite-budget
coverage of feasible CPU activity shapes over broad sampling and mutation?
Expressiveness means useful target coverage/error under a shared language and
budget, not program length or a language available exclusively to the agent.

Use the existing pinned Ibex simple system: RV32IM, fast multiply/divide,
instruction cache off, twelve event counters. This adds a programmable CPU
without a fourth RTL dependency. Expose operands, register dependencies,
multiply/divide, bounded loops, memory and conditional control flow. Preserve
the old Ibex adapter and all frozen source snapshots. Fixed-latency local RAM
and an in-order core are limitations; this is not a representative modern OoO
system, and cache/concurrency conclusions are out of scope.

The current DSL omits M-extension instructions and most operands and unrolls
loops. The new version must execute genuine loop branches and independently
check register and memory results. RTL and evaluator remain read-only.

## Feasibility gate before search

1. Build the pinned CPU in the managed container, into a separate writable cache.
2. Compile bounded programs and compare final architectural state with a
   software interpreter, including divide-by-zero, branches and memory effects.
3. Measure eight equal-duration bins inside one fixed CPU observation window;
   exclude initialization and result printing. Count core activity only, not RAM
   initialization or simulator instrumentation. Verify repeated-run identity.
4. Construct achieved witnesses from hand-specified instruction/operand families,
   independently of the competing random sampler. Check both distinct shapes and
   variation beyond a shared idle tail. If that fails, diagnose the interface
   before launching any model comparison.

The intended DSL has at most eight bounded segments with at most eight body
operations each. Total semantic body operations are fixed at 4,096; this is a
new hard non-idle constraint, not a change to the old frozen adapter. Report
retired instructions separately. Reserve a 200,000-cycle observation window;
completion beyond it is invalid, not a truncated score. This is a measurement
definition, not a wall-clock process timeout. Pilot runtime and memory use must
be measured before choosing the search matrix size.

## Comparative development protocol

Before comparative execution, commit a machine-readable manifest recording:
target witnesses and profiles, exact measurement scale, tolerance, seeds,
proposal budget, baseline generators/operators, prompt/model settings, tool
and source hashes. Use four target families if the feasibility gate supports
them, three development seeds (600–602), and initially sixteen proposed slots.
If evaluator cost requires a smaller matrix, record the reduction before runs.

Compare broad random sampling, structural/operand mutation with restarts,
and a feedback-driven full-program agent. Do not describe mutation as a
coverage-guided fuzzer unless an actual coverage signal guides it. All methods
use the same DSL, useful-work check, windows, feedback and proposal budget.
Missing, malformed and duplicate proposals consume requested slots; no free
model repair or hidden simulator calls. Every run retains its ledger and costs.

Primary descriptive endpoint: proposal-counted best-so-far target-error AUC.
Also report feasible targets solved, error per target, right-censored proposals
to tolerance, architectural validity, costs, and behavioral diversity at a fixed
budget. Use one corpus-fixed error scale, never per-candidate peak normalization.
Choose and record tolerance from repeatability and witness separation before
comparisons, not after observing which policy wins.

Targets and seeds in this pilot are development data. Do not use significance
tests to promote this small selected panel into a confirmatory result. A later
study needs fresh target families as well as fresh seeds, a frozen controller,
and appropriate multiple-comparison control. AES remains the bounded negative
case. Agent improvement is not a condition for reporting this pilot.

## Claim boundary

This pilot measures RTL activity. Ibex gate-level power validation is not yet
established; no temporal power superiority claim follows from a proxy win.
The workspace/anonymized-context ablation remains a separate possible step;
do not silently mix it with the hardware/interface change in this pilot.

## Frozen measurement and search details

Count unique core-net **bit transitions**, excluding clocks and CSR counters.
This differs from earlier bus-change proxies and is not numerically comparable
with their envelopes. The 1 ps waveform timescale is a simulator convention,
not a physical operating frequency. Waiting executes CSR reads and branches;
it is not clock gating. Register file and RAM outside the selected core scope
are not included. Verilator's two-state simulation is not an X-propagation proof.

The feasibility gate passed all architectural checks and exact repeated bit
counts. Four independent achieved profiles span 226.16–754.61 transitions per
edge across bins. One near-flat profile is an intentional control. Full source,
tool and target hashes are frozen in the results manifest before search.

Use sixteen slots, two shared initial programs, and batches of two. The agent
therefore receives seven feedback rounds, not a one-shot task. Run all sixteen
slots even after solving. AUC is trapezoidal over indices 1–16, with best error
capped at 1 (also the pre-valid-candidate error). Raw candidate errors remain
uncapped. Unsolved runs are right-censored at sixteen.

Random samples instruction families (including dense divide and memory bodies),
boundary operands, dependencies, segment counts and release cycles. Mutation
selects among the best four valid parents, changes operands/instructions/releases
or segment order, and restarts from that same sampler with probability 0.2.
Neither baseline receives witness programs. The agent sees anonymous target
vectors, complete schema, instruction semantics and compact trial feedback.

All policies share a content-addressed evaluator cache; hits and duplicates still
consume proposal slots. Malformed or missing model outputs consume their slots
without a free retry. Transport has a 120-second HTTP deadline but no process
alarm; simulation has no wall-clock timeout. Costs use the published Flash
estimate of $0.30/$2.50 per million input/output tokens, including thinking
tokens in output. This is estimated usage cost, not a billing export.
