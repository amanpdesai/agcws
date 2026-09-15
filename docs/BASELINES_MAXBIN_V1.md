# Frozen CPU baseline matrix — authorized 2026-09-15

Five designs: AES, DMA, Ibex, mesh, longer-window RedMulE. Nine unchanged
confirmation vectors per design (eight substantive profiles plus flat control),
seeds 9100–9109, phase-random and phase-GA: 900 cells, at most 115,200 slots.
The original engineering targets are exposed, not task-held-out.

Success: valid workload and maximum absolute bin residual divided by frozen
calibration width <=0.05. Budget 128, batch two, charged shared random initial
batch, stop at first successful batch. Record exact first hit, carry terminal
best RMSE to slot128 for AUC. RMSE continues to guide the existing GA; do not
retune it mid-run. Maximum-bin error separately governs solves and censoring.
Invalid slots count, receive no score; duplicates count. Flat controls remain
separate from substantive target aggregates. Incomplete cells remain explicit.

Strict feasibility is not established for every target under this new gate.
The user explicitly authorizes running these fixed tasks now. Unsolved requests
are not evidence of method failure on a proven-feasible task unless a strict
witness exists. Any later qualification searches remain separate and never
seed the baseline populations or change the vectors. All historical banks and
pilots remain unchanged.

18 cell workers per design, five concurrent designs. No provider calls and no
`--allow-paid`. The positive cost ceiling field is a schema requirement, not
permission for model use. CPU costs are not claimed to be zero.
New manifests record the all-bin gate/context changes; measurement source,
image and binary remain unchanged and are checked during preparation.
Only target vectors/scale enter manifests, never witness programs.

Run in tmux session `agcws-baselines-maxbin-v1`, one window per design. Logs:
`out/baselines-maxbin-v1/<design>/runner.log`. A 500-GiB free-disk guard stops
the relevant runner process group while preserving checkpoints; it is not a
time limit and does not delete data or automatically restart work.

Future Flash/Pro arms may reuse these baselines only with the identical task,
measurement contract, seeds, initializations, budget, batching and stopping
rule. Those paid runs are not part of this CPU-only launch authorization.
