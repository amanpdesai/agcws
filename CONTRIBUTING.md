# Contributing

AGCWS is both an experiment repository and a source of reusable CHIA nodes.
Keep changes reproducible, reviewable, and scoped to the documented research
plan.

## Before making changes

Initialize the pinned source dependencies:

```bash
git submodule update --init --recursive
```

Do not edit `tools/chia` in this repository. Changes intended for upstream
CHIA belong in a separate fork and should be extracted as focused commits.

## Local verification

Install the development environment and run the complete local gate:

```bash
make dev-install
make verify
make audit-reproducibility
```

The production boundary can be checked with:

```bash
docker build -t agcws:dev -f docker/Dockerfile .
make container-smoke
```

Use the task-specific Make targets for synthesis, evaluation, and analysis.
Record tool versions, input hashes, model identifiers, and prompt hashes in
generated provenance; never hand-edit result records to make a run pass.

## Source and experiment boundaries

- `src/agcws/nodes/` stays design-agnostic and reusable by CHIA.
- `src/agcws/adapters/` contains design-specific legality and elaboration.
- `flows/` wires nodes; `experiments/` owns sweeps and seeds.
- `analysis/` reads results and writes figures.
- Do not commit generated waveforms, build directories, credentials, or `.env`.

There is intentionally no GitHub Actions workflow. Required checks run locally
or inside the pinned Docker environment so EDA dependencies remain explicit and
portable.

## Research changes

Changes to a frozen tolerance, workload floor, prompt, dependency revision,
evaluator, or claim require a dated entry in `docs/DECISIONS.md`. Comparative
runs must use the same DSL, legality gate, evaluator budget, and history
surface for every policy.
