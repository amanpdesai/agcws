# agcws — Goal-conditioned workload synthesis

Synthesize legal hardware workloads toward requested activity profiles, with
gate-level power validation where available. Built around composable CHIA
stages, shared interfaces and proposal-counted comparisons.

## Results

The completed non-flat Ibex confirmation has 36 trajectories / 4,608 slots.
Pro solved 18/18 cases; phase-random solved 5/18. Earlier frozen Flash studies
on AES/DMA did not beat random. These are different study regimes.

[RESULTS.md](RESULTS.md) is the authoritative findings and limitations document.
[results/](results/) contains compact evidence, failures and accounting.
Large evidence trees are [losslessly packed](results/PACKED_EVIDENCE.md);
summaries remain readable and `make archive-audit` restores its inputs automatically.
Activity results are not automatically power results.

## Use

```bash
git submodule update --init --recursive
cp .env.example .env
make install
make test
make lint
make archive-check
make archive-audit
```

Configure local tools and Vertex credentials only in `.env`/ADC. The commands
above do not launch experiments. There is no GitHub CI workflow.

One study entry point: `python -m agcws.pipeline`. See
[pipeline commands](docs/PIPELINE.md), [architecture](docs/ARCHITECTURE.md),
[tools](docs/TOOLS.md) and [next steps](docs/PLAN.md).

## Layout

- `src/agcws/pipeline/`: shared runner, policies and Ibex temporal backend.
- `src/agcws/{nodes,adapters,goals,telemetry}/`: measurement contracts.
- `scripts/`, `validation/`, `flows/`: hardware stages, GLS/window power, CHIA.
- `docker/`: tool environment and bounded container lifecycle.
- `results/`: published evidence; `out/`: ignored scratch.
- `archive/`: exact historical source, protocols, reports and original tests.

Historical studies use the [isolated source archive](archive/README.md), not
competing active runners. Third-party dependencies retain their own licenses;
project terms are in [LICENSE](LICENSE).
