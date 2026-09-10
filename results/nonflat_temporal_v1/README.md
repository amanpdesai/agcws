# Non-flat temporal confirmation archive

Status: construction/qualification in progress; **no comparative result yet**.
Protocol: [NONFLAT_TEMPORAL_V1_PROTOCOL.md](../../docs/NONFLAT_TEMPORAL_V1_PROTOCOL.md).

Three targets, six fresh seeds, Pro-4096 versus phase-random, 128 charged slots:
36 trajectories / 4608 slots, at most 1134 model calls. $150 liability ceiling.
Targets must have independently checked legal witnesses, constant-vector floor
>=0.20 and pairwise distance >=0.15. Failed qualification stops before paid calls.
The frozen model/controller is unchanged from depth development. Witness programs
are retained as evidence but never enter model payloads.

`manifest.json` freezes construction, sources, runtime, budget and settings;
`witnesses.json` retains all 24 attempts; `targets.json` records first qualifying
targets; `search_manifest.json` binds targets and every cell. Each is committed
before its dependent stage. `smoke_pass.json` is the independent four-slot CPU
integration gate, not comparative data. `panel/` and `evaluations/` receive
compressed records after each completed cell. `summary.json` exists only after
complete-panel audit. No VCD/FST is committed.

## Operation

The supervisor is the user service `agcws-nonflat-temporal-v1.service`, with
linger enabled and automatic restarts disabled. Scratch checkpoints and the
service log are under `out/nonflat-temporal-v1/`. Service launch evidence will
be added only after a running PID and actual model response are verified.

```bash
systemctl --user status agcws-nonflat-temporal-v1.service
tail -n 20 out/nonflat-temporal-v1/service.log
.venv/bin/python -m analysis.status_ibex_depth_v1 --root out/nonflat-temporal-v1
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m experiments.nonflat_temporal_v1.study audit
```

Status reports are counts/errors/cost, not interim efficacy analysis. An absent
`summary.json` is not completion. Failure records and request reservations must
be resolved explicitly before restart; never delete them to force resampling.
Use the same frozen `study run` entry point to resume resolved checkpoints.
Full success writes `out/nonflat-temporal-v1/complete.json`; the service's final
exit code separately distinguishes execution failure from completion.
