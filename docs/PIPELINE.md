# Maintained study pipeline

Install dependencies with `make install`. Local tool paths and credentials
belong in the ignored `.env`; start from `.env.example`. Never commit ADC files.

Read-only commands (no simulation or model calls):

```bash
make archive-check
make archive-audit
PYTHONPATH=src .venv/bin/python -m agcws.pipeline evidence-check
PYTHONPATH=src .venv/bin/python -m agcws.pipeline --help
PYTHONPATH=src .venv/bin/python -m agcws.pipeline validate --config configs/study.example.json
```

The example is a configuration-shape example, not a pre-registered study or
witnessed target bank. Backends are `ibex-temporal`, `aes-temporal` and
`dma-temporal` and `mesh-temporal`. AES/DMA have new source-built schedule ports under engineering
verification, not yet qualified target banks or completed Flash smokes.
The mesh port uses compact traffic phases, not the AES/DMA work/wait grammar.
RedMulE is not yet registered as a runnable temporal backend.

Mesh phases control release start/duration, packet count, source set, routing
pattern and data pattern, with global sink pacing. The receiver checks all packet
IDs/data/destinations. Its observation is eight reset cycles plus 8,192 traffic
cycles, including drain time. At least 64 packets must complete. Random samples
1–32 phase allocations; its GA uses tournament selection, phase crossover,
insert/delete/field mutation and 20% immigrants. Static or completion failures
consume proposals without scores; unknown tool failures stop the run. The initial
CPU check is not a qualified target bank or a provider smoke.

Ibex takes an explicit simulator `binary`. AES/DMA require `binary: null`:
the pinned image and source inventory identify container-built simulators.
Their current contract is 64 work units and 6,000 idle cycles (AES: one block;
DMA: one 64-byte copy), with fixed observation windows of 6,774 and 12,000
clock edges respectively. These are development contracts, not frozen paper
settings. AES uses a locked, content-keyed build cache. DMA uses independent
per-replay Icarus build directories. No host simulator is used.

Schedule ports expose one shared grammar/context template and support random,
phase-random, phase-GA, Flash and Pro dispatch. Only CPU checks are complete so
far; provider schema acceptance still needs a bounded Flash smoke. The schedule
GA combines work partitions, idle partitions and ordering from selected parents,
then applies a legal structural mutation, with 20% random immigrants. This is
a schedule-specific GA, not an unchanged replication of the Ibex phase GA.
Unsupported GeST/screening arms are rejected rather than silently substituted.

For packed historical evidence, use `evidence-extract --study STUDY --destination
/absolute/new/review` to reconstruct a read-only-use review workspace with original
paths. See [packing and recovery](../results/PACKED_EVIDENCE.md). `archive-audit`
does this automatically for the completed non-flat study.

Supply explicit named eight-bin rates, scale, tolerance, seeds, policies,
budget, batch size, simulator and image. GeST/screening controls require their
declared batch-four panel; `gest-batch2` explicitly changes feedback frequency.

New configurations may set `stop_on_success: true`: stop after the first batch
with a valid tolerance hit, charge all siblings, and carry the terminal best
error forward for budget-axis AUC. The summary records actual charged slots and
the exact first-hit slot. Omission retains historical full-budget behavior.
`max_workers` bounds concurrent independent cells; optional `provider_workers`
bounds simultaneous model calls (default one). Atomic reservations enforce the
global model-cost ceiling even while calls overlap. Set both limits explicitly
for new parallel studies. Neither option changes within-trajectory feedback.

For a separately authorized future study:

```bash
PYTHONPATH=src .venv/bin/python -m agcws.pipeline prepare --config reviewed-study.json --directory out/new-study
PYTHONPATH=src .venv/bin/python -m agcws.pipeline run --directory out/new-study --execute --allow-paid
PYTHONPATH=src .venv/bin/python -m agcws.pipeline status --directory out/new-study
PYTHONPATH=src .venv/bin/python -m agcws.pipeline export --directory out/new-study --destination results/new-study
PYTHONPATH=src .venv/bin/python -m agcws.pipeline verify-export --directory results/new-study
```

Run in the foreground or under an explicitly configured supervisor; the CLI
does not detach. Repeating `run` verifies immutable checkpoints and source/runtime
identity. A request marker without a response halts rather than buying an
unknown duplicate. Never delete it to force progress. API failures retain
diagnostics and reserved cost.

Docker stages use the prepared image digest, `--rm`, `--init`, a read-only
checkout, explicit output bind mount and bounded logs. Toolchain/simulator
build is preparation work. The controller runs on the host; compilation and
simulation run in the container.

Exports are deterministic compressed compact records, not VCDs or simulator
binaries. Export never deletes scratch; retention is separate maintenance.
A scientific claim still needs its frozen protocol and declared inference.
For completed studies use [archive-audit](../archive/README.md), not the new
runner. This consolidation does not rewrite historical manifests or rerun
research. Active orchestration is tested with fake providers/evaluators.
