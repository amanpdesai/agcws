# GeST/SAGA integration qualification — 2026-09-10

Scope: source inspection and isolated component checks. Neither full optimizer
nor remote measurement runner has been executed. No paid calls or new simulator
comparisons. This is the first slice of [the roadmap](UPSTREAM_BASELINES_PLAN.md).

## Pins and notices

| Submodule | Upstream | Revision | Permission notice |
|---|---|---|---|
| `third_party/gest` | `toolsForUarch/GeST` | `4fbe3e4549740dcceaf8a968bd0156ce8cbe5643` | `README` and original source headers |
| `third_party/gest_saga` | `ucy-xilab/GeST-SAGA` | `2292814234735680ccab4f0cba567017e4ca425c` | `README_SETUP.md` and original source headers |

The setup notices contain MIT permission text with ARM/University of Cyprus
attribution. Preserve them and check notices on any individual file adapted.
Both source trees remain unchanged. HTTPS submodules pin actual source, not a
paper-derived reimplementation. Repository discovery does not verify paper
performance claims.

## Code-level integration map

| Interface | Upstream implementation | Required bridge / concern |
|---|---|---|
| Genotype | `Instruction.py`, `Operand.py`, `Individual.py`; XML instruction definitions | Assembly-oriented fixed-length sequence. Our variable phase releases/work allocations need an explicit encoding and support audit. |
| Fitness | `Fitness/DefaultFitness.py`, `Population.getFittest` | Maximizes the first measurement. Negative temporal loss preserves tournament ordering, but is not safe to assume for roulette or logarithmic fitting. |
| Operators | `Algorithm.__mutation__`, `__uniform_crossover__`, `__onePoint_crossover__` | Instruction replacement and fixed `loopSize` crossover; not equivalent to our phase insertion/deletion GA. |
| Runner | `Algorithm.measureTrainingGeneration`, `measureQuickGeneration`, `measurePopulation` | Owns synchronous population execution and repeated measurements. Replace execution boundary with explicit proposal ledger; never invoke it as an unaccounted inner loop. |
| Measurement | `Measurement/Measurement.py`, `MeasurementLikwidPower.py` | SSH, compilation and physical power measurement are not our Verilator evaluator. No remote credentials or sudo setup should be copied. |
| SAGA features | `featureExtraction.instructionTypesAsFeatures` | Global instruction-type counts, without order or release timing. Reordered sequences have identical features. |
| SAGA prediction | `PredictReferenceFeatures.getReferenceFeatures` | Fits feature values as logarithmic functions of measured fitness, then extrapolates at maximum observed fitness plus 100. This is not a generic temporal-loss regressor. |
| SAGA score | `MeasurementLikwidPower.SF_fitness` | Negative distance from predicted feature proportions/total count, not measured power or temporal loss. Must never enter the measured best-so-far archive. |

## Concrete hazards found

- GeST and SAGA instruction constructors differ: SAGA requires an additional
  `numOfInstructions` field. The isolated checks dispatch by pinned version;
  this is an explicit API difference, not an exception-driven fallback.

- Training and quick-generation paths retry `ValueError`/`IOError` indefinitely.
  The bridge must charge and expose failures, without hidden retry loops.
- Crossover-disabled evolution appends parent objects directly before mutation;
  this can mutate historical parent state. Population construction can exceed
  nominal size by adding both children. Audit copying and every produced slot.
- The predictor catches failed fits and substitutes zero features. This cannot
  silently become a successful surrogate observation in our flow.
- The three candidate log bases are the same two-parameter functional family
  under rescaling; do not describe them as three independent model classes.
- Negative error cannot simply be fed into logarithms. Changing fitness scale,
  extrapolation offset or temporal features is an algorithm adaptation requiring
  development selection and a new freeze, not a faithful zero-change port.
- Upstream uses mutable constructor defaults; the component checks always pass
  explicit lists. Do not rely on default shared state in the bridge.
- Modules use top-level imports. Isolated processes avoid GeST/SAGA name clashes.
  `Algorithm.py` imports Paramiko and legacy `visa`; SAGA prediction also needs
  NumPy/SciPy. SciPy is absent from the current project environment. Full runner
  and curve-fit execution are therefore not claimed by this slice.

## Executed component checks

`tests/test_upstream_baseline_components.py` checks exact pins and runs fresh
isolated Python processes. Both versions exercise instruction rendering, deep
copy isolation, measurement-to-fitness passthrough and maximizing population
ordering. A SAGA test calls the actual feature extractor on two reordered
sequences and confirms identical features. These tests do not import Algorithm,
execute assembly, unpickle external files or connect to hardware.

Run with initialized submodules:

```bash
.venv/bin/python -m pytest -q tests/test_upstream_baseline_components.py
```

## Next implementation checklist

1. Keep original Pro/random confirmation unchanged and separately frozen.
2. Build a versioned ask/tell bridge outside these source trees. Declare fixed
   versus variable phase support, preserve immutable history and handle each
   generated child within the proposal budget.
3. Start with GeST operators, shared compiler/validator/evaluator, tournament
   selection and documented maximize-compatible temporal fitness. Test candidate
   reconstruction, invalid charging and budget edges before a CPU-only smoke.
4. For SAGA, retain a named upstream-feature control, then develop a separately
   named temporal-feature adaptation. Fit only previously measured training data;
   distinguish surrogate ranking from real observations. Reject fit failure
   explicitly rather than substituting a policy or successful zero score.
5. Pin dependencies in an isolated container once the chosen integration path
   is known. Do not install hardware drivers into the shared host.
6. Freeze proposal and simulator-call accounting, hyperparameters, witness
   construction and target selection before the development comparison. No
   superiority or published-algorithm reproduction claim follows from this audit.
