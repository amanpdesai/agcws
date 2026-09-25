# Architecture and workflow

The system searches for executable workloads that match a requested RTL activity
profile. A separate replay stage estimates the power of selected workloads.

```text
  Task specification
  design + target + work + measurement + budget
                  |
                  v
  +-------------------------------+
  | 1. Activity-guided search      |
  | propose -> simulate -> score  |
  |    ^                    |     |
  |    +----- feedback -----+     |
  +---------------+---------------+
                  | recorded workloads and outcomes
                  v
  +-------------------------------+
  | 2. Select and freeze workload |
  +---------------+---------------+
                  |                 Reference workload
                  v                         |
  +-----------------------------------------v--+
  | 3. Mapped replay and OpenSTA power estimate |
  +---------------------+----------------------+
                        v
              4. Reports and evidence
```

Power estimates do not feed back into the studied search loop.

## 1. Search

Each design adapter defines its workload language and translates proposals into
simulator inputs. AES, AXI DMA, Ibex, BaseJump mesh and RedMulE use different
interfaces but share the evaluation loop and measurement contract.

```text
  Policy -> schema/protocol checks -> RTL simulation -> completion checks
    ^                |                                      |
    |                +-- rejection reason                   +-- activity
    |                         |                                  |
    +---------------- recorded outcome and interval errors -----+
```

The evaluator accepts a match only when execution and required work pass and
every interval meets its tolerance. RMS error tracks search progress. The final
study uses eight intervals, tolerance 0.05 and a 128-proposal budget.
See [experiment setup and results](RESULTS.md#evaluation-setup).

Classical and LLM policies propose workloads, not RTL changes. The evaluator
determines validity and error. Returned invalid proposals and duplicates consume
slots. Provider failures have separate attempt and recovery records rather than
being treated as measured workload failures in the recovery-enabled runner.

## 2. Selection

Select the valid workload with the smallest maximum-bin error from each run.
Break ties by RMS error, then proposal order. Unsolved runs contribute their best
valid attempt. All-invalid runs remain missing. Freeze the selection before power
assessment so power cannot influence which workload is chosen.

## 3. Power assessment

```text
  RTL + cell library -> cached synthesis -> mapped netlist
                                                 |
  Selected workload or reference -> gate simulation -> window activity
                                                           |
                                                           v
                                                  OpenSTA estimates
                                                           |
                                            aligned reference comparison
```

All five designs have completed replay collections. Candidate and reference use
matched netlists, libraries, clocks and windows. Checks cover functional replay,
alignment, annotation and switching reconstruction. Ibex retains estimates under
the documented reconstruction exception, with errors preserved per case.

Estimated dynamic power is internal plus switching power. The 10 ns reference
clock is a characterization assumption, not demonstrated timing closure.
Zero-delay replay does not capture routed parasitics or delay-induced glitches.
Reference-power agreement is distinct from activity-target acceptance.

## 4. Commands and outputs

Run from the checkout after [installation](TOOLS.md). These examples inspect or
prepare work without launching simulations or paid calls.

```bash
python -m agcws doctor
python -m agcws study status --directory out/STUDY
python -m agcws study prepare --config CONFIG.json --directory out/NEW_STUDY
python -m agcws evidence verify --study results/STUDY
python -m agcws power --help
python -m agcws report --help
```

Use the installed environment's Python. Execution requires `study run --execute`,
and model policies also require `--allow-paid`. Preparation alone does not launch
a study. Use each command's `--help` for its arguments.

| Location | Contents |
|---|---|
| `out/` | Local builds, caches and run checkpoints |
| `results/` | Frozen summaries, manifests and compact evidence |
| `paper/` | Manuscript, extraction scripts, figures and Overleaf export |

Resume with the study's verified runtime and checkpoints, not arbitrary current
code. Preserve failed attempts and unknown-cost records. Do not edit archived
manifests or change measurement rules to make a replay pass.

## Code ownership

All packages below live under `src/agcws/`.

| Package | Responsibility |
|---|---|
| `cli`, `core` | Commands, configuration and shared contracts |
| `designs` | Workload languages, adapters and harness assets |
| `baselines` | Classical proposal policies and surrogate screening |
| `search`, `studies` | Policy dispatch, model transport, execution and checkpoints |
| `evaluation` | RTL activity, synthesis, gate replay and power |
| `reporting`, `evidence` | Analysis, plotting, archive verification and restoration |
| `integrations/chia` | CHIA bindings for shared stages, distinct from the frozen benchmark measurement path |
