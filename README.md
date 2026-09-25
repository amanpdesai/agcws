# agcws: Goal-conditioned workload synthesis

Synthesize legal hardware workloads toward requested activity profiles, with
gate-level power validation where available. Built around composable CHIA
stages, shared interfaces and proposal-counted comparisons.

## Results

The completed five-design comparison evaluates three classical policies,
Gemini 3.5 Flash-Lite and Gemini 3.8 Flash under a shared 128-proposal budget.
Gemini 3.8 meets the every-interval activity tolerance in **387/400 nonflat
runs**, compared with 46 for Flash-Lite and 1, 4 and 33 for the classical
policies. Near-flat controls are reported separately.

The separate mapped-gate assessment is also complete across all five designs.
Selected Gemini 3.8 workloads have lower mean error against designated reference
power profiles than the best classical comparator on each design. Reference
agreement is not a power-target success criterion.

See [final results](docs/RESULTS.md) for tables, interpretation and evidence links,
or read the [paper](paper/report.pdf). [Published evidence](results/README.md)
retains compact measurements, failures and accounting in per-design archives.

## Use

See [architecture and workflow](docs/ARCHITECTURE.md) for the execution stages
and [tools](docs/TOOLS.md) for dependencies.

```bash
bash tools/setup.sh
cp .env.example .env
make install
make test
make lint
.venv/bin/agcws --help
.venv/bin/agcws doctor
```

Configure local tools and Vertex credentials only in `.env`/ADC. The commands
above do not launch experiments. There is no GitHub CI workflow.

One command entry point: `agcws` (or `python -m agcws`). See
[architecture and commands](docs/ARCHITECTURE.md) and [tools](docs/TOOLS.md).

## Layout

- `src/agcws/studies/`: shared runner, checkpoints and target qualification.
- `src/agcws/baselines/`: classical proposal policies and surrogate screening.
- [Package map](src/agcws/README.md): code ownership and measurement boundaries.
- `src/agcws/search/`: shared policy dispatch and model transport/recovery.
- `benchmarks/`: pinned hardware sources and shared design dependencies.
- `src/agcws/designs/`: five design interfaces, simulators and harness assets.
- `src/agcws/evaluation/`: activity, synthesis, waveforms and gate power.
- `src/agcws/reporting/`: reusable statistics, audits and plots.
- `src/agcws/evidence/`: verification, packing and restoration.
- `src/agcws/integrations/chia/`: framework nodes and integration checks.
- `tools/`: pinned tool source submodules and build dependency lock.
- `paper/figures/`: paper-specific figure recipes, not analysis implementations.
- `docker/`: tool environment and bounded container lifecycle.
- `results/`: published evidence; `out/`: ignored scratch.

Historical implementations remain in Git history, not in the active release.
Third-party dependencies retain their own licenses.

The final studies are complete. Archived runs retain their recorded runtime
identities. Use those identities for historical replay, not the current checkout.
