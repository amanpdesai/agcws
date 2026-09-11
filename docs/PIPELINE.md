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
witnessed target bank. Only `ibex-temporal` is a maintained study backend.
DMA/AES cross-design execution is planned, not implemented by changing this
backend name. Historical adapters and tools remain available for a tested port.

For packed historical evidence, use `evidence-extract --study STUDY --destination
/absolute/new/review` to reconstruct a read-only-use review workspace with original
paths. See [packing and recovery](../results/PACKED_EVIDENCE.md). `archive-audit`
does this automatically for the completed non-flat study.

Supply explicit named eight-bin rates, scale, tolerance, seeds, policies,
budget, batch size, simulator and image. GeST/screening controls require their
declared batch-four panel; `gest-batch2` explicitly changes feedback frequency.

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
