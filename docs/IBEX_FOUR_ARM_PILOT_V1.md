# Authorized four-arm integration pilot

2026-09-15: user authorizes one Ibex target, two seeds, phase-random, phase-GA,
Flash and Pro, with a combined $10 estimated model-liability ceiling.

Use bit-activity-v2 confirmation-alternating (constant-vector floor 0.4), seeds
9500–9501, 128 slots, batch two, tolerance 0.1 and first-success-batch stopping.
Eight cell workers, two provider workers, one shared atomic cost meter. Preserve
unknown-call reservations. Ceiling exhaustion halts the study, not a license
to spend more. This is a software estimate, not a Google billing hard limit.
No automatic restart, extra attempts, model substitution or larger study.

Both models use 4096 thinking tokens and otherwise frozen existing settings.
Only target rates and the fixed scale enter the run; bank witnesses are never
copied into the runtime manifest. Two shared random initializations are charged
to each arm. Existing bank verification matches the current source/runtime
fingerprint before preparation. This pilot uses exposed engineering targets
and is not paper inference or controller selection.

Operational acceptance: inspect all eight terminal cells; recompute AUC,
validity, early-stop/censored counts and ledger liability; confirm generated
measurements enter subsequent model history where calls continue. A run solved
by initialization may never call its model and cannot certify that provider.
Retain API and parse failures, and archive exact compact evidence. A policy
need not solve the target for its execution to be correct.

Launch: `tmux` session `agcws-ibex-pilot-v1`, via
`bash scripts/run_ibex_four_arm_pilot.sh`. Log:
`out/ibex-four-arm-pilot-v1/runner.log`. Terminal marker:
`AGCWS_PILOT_EXIT_CODE=0` means the runner finished, not that the audit passed.
