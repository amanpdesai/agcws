# Clean three-arm baseline restart

## Status and scope

On 2026-09-16 the user requested a clean implementation state across all arms,
not a mixture of reused measurements and new code. The old `baselines-maxbin-v1`
panel is historical. Its incomplete Ibex runner was terminated; no old cells or
evaluation caches will enter this panel. The task vectors, scales, useful-work
requirements, windows, 128-slot budget, batch size 2, and every-bin ≤0.05
acceptance stay unchanged. RMSE remains the reported AUC metric. GA retains its
old RMSE selection; the new policy selects against worst-bin residuals.

Three arms: `phase-random`, `phase-ga`, `phase-model`. The last is a
literature-informed adaptation, not PaTGen, SAGA, or GeST reproduced verbatim.
This protocol is post-hoc methodological development; earlier confirmation
results have been observed. Do not call a repeat on the same bank a fresh
independent held-out confirmation.

## New policy, frozen candidate version

`phase-model-v1` fits an eight-output ridge model to the current cell's measured
signed residuals. Its 33 fixed descriptors describe approximate phase occupancy
and hashed operation categories; they are not a physical power model. No
calibration witnesses, sibling cells, confirmation solutions, or model calls are
available to the policy. Bootstrap until eight valid observations; every eighth
slot is an explicit random immigrant.

For each other slot, form 32 internal candidates: one quarter structural GA
offspring, the remainder small timing/resource transfers from up to eight
max-bin-ranked parents. AES/DMA transfers preserve exact work/idle totals.
Predict residuals and minimize their maximum absolute value plus 0.05 times
distance to the nearest observed feature vector. Ridge regularization is 0.1;
the intercept penalty is 1e-8. Duplicate candidates are excluded from the
internal pool; an exhausted pool triggers a recorded random exploration step.
There is no numerical-error fallback or free simulator retry.

Only the selected workload is submitted to the common evaluator. It consumes
one proposal slot even if invalid. Internal surrogate candidates, training
slots, predicted residuals and selected identity are recorded per decision.
Report internal model evaluations separately: 128 submitted proposals does not
mean identical optimizer CPU effort. Surrogate fit and internal ranking use no
extra simulations; all simulator measurements originate in charged slots.

## Literature basis and limits

PaTGen (Yin et al., TACO 2026, DOI 10.1145/3816437), §§3.3–3.4, combines
SLSQP-based block composition with GA-based delay optimization to reproduce
CPI/MPKI traces. It is software proxy benchmarking, not arbitrary RTL stimulus
or dynamic-power targeting. Its profiled additive model is not assumed valid
for our pipelines/backpressure. We borrow separation of structure and timing,
not its model, loss weights or published evaluation claims.

SAGA motivates cheap learned ranking between measured evaluations. The HPCA
2026 di/dt study motivates parameter-specific, constraint-aware operators.
Neither makes our adaptation a novel search algorithm. Our research comparison
is agent versus stronger conventional search under a shared task contract.

## Verification and launch gates

1. Unit tests: all five representations, deterministic replay, history isolation,
   exact AES/DMA resource conservation, finite inputs and no hidden simulations.
2. Development smoke: one alternating **development** target, seed 9300,
   12 slots, three arms, all five designs. No LLM calls. This is execution and
   storage validation, not evidence the new optimizer outperforms anything.
3. Full tests and lossless waveform-retention verification.
4. Prepare a fresh full plan with `scripts/prepare_baseline_matrix.py` after
   verification. All manifests must share one source state; record the Git
   commit and container digest. No runtime edits during execution.
5. Full execution requires a separate launch decision. Do not start it as a
   side effect of preparation. Old output and archives are never cache inputs.

The development command is `scripts/prepare_baseline_matrix.py --development-smoke`;
run each design via `scripts/run_baseline_design.py DESIGN --panel baselines-model-v1-dev`.
Full preparation creates `results/DESIGN/baselines-model-v1-plan/` and fresh
`out/baselines-model-v1/DESIGN/`. The full panel has 1,350 cells, not 900.

Verification completed: all fifteen development cells finished (180 charged
proposals, zero API calls); all five packed evidence exports were restored and
byte-verified. See [smoke report](../results/baselines_model_v1_dev/README.md).
The full plan is prepared against runtime commit `a025d4f9f`, with repository
files checked against Git, dependencies against submodule pins, and generated
RedMulE dependency files separately content-hashed and unchanged from the prior
reference. Docker image and simulator hashes remain unchanged. No full cells
have started. Strict ≤0.05 feasibility is still not established for every target.

## Storage lifecycle

Containers already use `--rm`; host-bound artifacts caused the growth. After a
result checkpoint, the evaluator retires each expanded VCD losslessly under the
evaluation lock. If an FST exists, regenerate its VCD and compare SHA-256 and
length before deleting the expanded copy. Otherwise compress with zstd and
verify exact decompression. Retain the compressed trace and a hash receipt.
Conversion, hash mismatch or changed files fail closed. A cache hit retries
unfinished retention, not the simulation. Incomplete uncheckpointed attempts
remain untouched by automatic retention.

`maintenance/retire_baseline_panel.py` is an explicit migration for the old panel:
hold runner locks, refuse active mounted containers, archive and verify compact
evidence per design, then retire only exact VCD paths with `find -delete`.
No original FSTs or compact evidence are deleted. Archives and receipts remain
under `out/retired-baselines-maxbin-v1/`; per-waveform retention receipts stay
beside their compressed traces. This operation is not a blanket `out/` purge.

Restore an exact VCD for further analysis with
`python maintenance/restore_waveform.py PATH.vcd.retention.json NEW_PATH.vcd`.
Both compressed and decompressed hashes are checked; existing output files are
never overwritten. Ordinary pipeline reads use cached activity/feedback JSON
and do not need to restore waveforms.
