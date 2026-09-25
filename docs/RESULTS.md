# Final results

Gemini 3.8 Flash matches the requested activity in **387 of 400 nonflat runs
(96.75%)**, compared with 46 for Flash-Lite and at most 33 for any single
classical policy. Selected workloads also have lower mean error against
designated reference power profiles under the separate mapped-gate assessment.

This page summarizes the final comparison in the [paper](../paper/report.pdf).
Development studies, pilots and superseded experiments are not included.

## Evaluation setup

Each of five designs has eight fixed nonflat activity targets and one near-flat
control. Ten search seeds give 80 nonflat runs per design and policy, or 400
across all designs. The 50 control runs per policy are reported separately.

Policies share the task, evaluator, workload schema, two initialization proposals
for each task and seed, and a maximum of 128 charged proposals. A workload solves
the task only if it executes correctly, meets its work and deadline requirements,
and has normalized absolute activity error no greater than **0.05 in every one
of eight observation intervals**. Normalization uses a fixed calibration span
for each design. This is not a 5% power-error criterion.

The classical policies are phase-random, phase-GA and phase-model, a
surrogate-guided search policy. The LLM configurations are Gemini 3.5 Flash-Lite
and Gemini 3.8 Flash, both using MEDIUM reasoning, with output-token ceilings
of 8,192 and 65,536 respectively. These comparisons do not isolate model identity
or reasoning. On Mesh, classical policies retain sink period 8 and pauses from
0 to 3, while the LLM schema permits wider settings.

## Activity tracking

The table reports mean area under the best-so-far normalized RMS-error curve
(AUC) over the 128-proposal budget. Lower is better. Early-stopped runs carry
their best error forward to the end of the budget. Solve counts measure the
stricter every-interval criterion, not average error.

| Design | Random AUC | GA AUC | Phase-model AUC | Flash-Lite AUC | Gemini 3.8 AUC |
|---|---:|---:|---:|---:|---:|
| AES | 18.43 | 19.60 | 12.13 | 17.38 | **1.23** |
| DMA | 32.80 | 33.11 | 30.17 | 40.52 | **3.72** |
| Ibex | 44.86 | 41.75 | 46.91 | 51.31 | **4.86** |
| Mesh | 36.50 | 31.41 | 32.76 | 24.62 | **2.24** |
| RedMulE | 45.72 | 37.83 | 46.57 | 40.63 | **5.33** |

Each per-design solve count below is out of 80 nonflat runs.

| Design | Random | GA | Phase-model | Flash-Lite | Gemini 3.8 |
|---|---:|---:|---:|---:|---:|
| AES | 1 | 2 | 33 | 21 | **80** |
| DMA | 0 | 1 | 0 | 1 | **78** |
| Ibex | 0 | 1 | 0 | 4 | **80** |
| Mesh | 0 | 0 | 0 | 20 | **80** |
| RedMulE | 0 | 0 | 0 | 0 | **69** |
| **Total / 400** | **1** | **4** | **33** | **46** | **387** |

Gemini 3.8 reduces mean AUC by **85.9% to 92.9%** relative to the
lowest-AUC classical policy on each design. It is the only evaluated policy to
solve nonflat RedMulE requests. Flash-Lite's advantage is more limited: it
solves Mesh cases missed by the classical policies, but has worse mean AUC
than every classical policy on DMA.

Across the 400 nonflat runs, Gemini 3.8 uses **6,008 charged proposals**,
compared with 47,678 for Flash-Lite and 49,290 to 51,088 for the classical
policies. Counts include initialization and unsuccessful runs. They measure
submitted search effort, not model calls, simulation time or cost.
Across all designs, Gemini 3.8 solves 50/50 near-flat controls and Flash-Lite
solves 23/50. Controls are excluded from both tables above.

Paired comparisons use ten seed-level differences per design, averaging over
its eight targets within each seed. All 15 Gemini-versus-classical AUC
comparisons favor Gemini after adjustment for multiple comparisons
(adjusted p = 0.0293). These results describe repeated search on the fixed,
previously observed target bank, not generalization to unseen designs or targets.

### Mesh sink-setting sensitivity

Fixing sink period to 8 and clamping pauses to 0–3 changes 13 Flash-Lite
and three Gemini finalists. All 16 changed workloads pass RTL, gate replay,
annotation and strict switching reconstruction. The 164 already-compatible
finalists reuse their unchanged measurements.

| Mesh result | Original | Restricted |
|---|---:|---:|
| Gemini nonflat matches | 80/80 | 80/80 |
| Flash-Lite nonflat matches | 20/80 | 20/80 |
| Gemini control matches | 10/10 | 10/10 |
| Flash-Lite control matches | 7/10 | 6/10 |
| Gemini nonflat reference-power error (%) | 0.66971 | 0.66966 |
| Flash-Lite nonflat reference-power error (%) | 1.38145 | 1.38223 |

This is post-search replay of fixed finalists, not a restricted-policy search.
It does not revise the search AUC or proposal counts. The
[sensitivity evidence](../results/mesh/sink-sensitivity/README.md) preserves
both results and the exact intervention.

## Estimated power against reference workloads

Search uses RTL activity, with no gate-power feedback. After search, one valid
workload per run is selected by maximum-bin activity error, breaking ties by
RMS error and proposal order. Selected workloads and separately specified
references are replayed under matched netlist, library, 10 ns clock and
observation conditions. OpenSTA estimates internal and switching power.

The table reports **mean normalized RMS error against the reference workload's
power profile, expressed as a percentage**. Each run's eight-interval RMS
candidate-minus-reference error is divided by the reference's duration-weighted
mean dynamic power. Lower is better. Profiles are not shifted or independently
rescaled, and both columns use the same measured task/seed pairs.

| Design | Gemini 3.8 error (%) | Classical error (%) | Classical comparator | Matched pairs |
|---|---:|---:|---|---:|
| AES | **0.956** | 8.675 | Phase-model | 80 |
| DMA | **0.076** | 1.031 | Phase-model | 80 |
| Ibex | **14.481** | 36.848 | Phase-GA | 80 |
| Mesh | **0.670** | 1.559 | Phase-GA | 80 |
| RedMulE | **6.143** | 24.364 | Phase-GA | 80 |

The comparator is the classical policy with the lowest observed mean power
error for that design. Gemini 3.8 has lower mean reference-power error on every
design, without power feedback during search. Each comparison uses all 80
nonflat runs per policy.

The references are concrete workloads, **not prescribed watt-valued targets**.
All 40 nonflat references meet the unchanged activity criterion. References were
constructed separately against the fixed activity targets, without using policy
finalists, and frozen before power comparison. Each is one realization of its
activity target, not a unique conversion to watts. Of 400 nonflat Gemini profiles, 399 improve on
their reference's best constant approximation, its eight-bin mean. DMA references
have only 3.0% to 4.3% peak-to-trough variation relative to mean power, so a
small normalized error alone would not establish close temporal tracking.

All 2,250 finalists and 45 references yield validated estimates. For Ibex and
RedMulE, per-case audits explain discrepancies caused by OpenSTA's switching-rate
cap without changing native power values. No power measurements remain excluded.

## Final evidence

- [Classical baseline summary](../results/summaries/baselines.json)
- [Flash-Lite summary](../results/summaries/flash_lite.json)
- [Gemini 3.8 summary](../results/summaries/gemini_3_8.json)
- [Completed power summary](../results/summaries/power.json)
- [Paper source](../paper/report.tex)
- [Per-design archives and verification](../results/README.md)

Final summaries and archived measurements support the numbers above. Historical
evidence remains in Git history.
