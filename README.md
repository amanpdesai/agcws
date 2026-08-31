# Agentic Goal-Conditioned Workload Synthesis

Given RTL, a legal stimulus interface, and a target dynamic-power profile, an agent synthesizes semantically valid workloads toward that behavior. Targets may be scalar, compositional, or coarse temporal.

Built as a composable [CHIA](https://github.com/ucb-bar/chia) loop for the A³ CHIA Hackathon (MICRO 2026).

## Status

Under active development (2026-08-29 → 2026-09-20). The AES oracle and
bounded search path are runnable; DMA/Ibex adapters and comparative studies
remain in progress.

See `docs/ARCHITECTURE.md` and `docs/PLAN.md`.

Install the optional plotting dependency with `make analysis-install` before
running `make plot-activity` in a fresh environment.

## Common tasks

The Makefile is a thin operator surface over the reproducible scripts:

```bash
make test
make verify
make inspect-liberty
make synth-aes
make evaluate-aes
make research-smoke
PYTHONPATH=src python scripts/run_aes_task.py \
  experiments/workloads/aes_min_scored.json out/aes-core-synthesis-final4
```

Override `SYNTH_DIR`, `WORKLOAD`, and `EVAL_DIR` for separate task roots;
tool and Liberty paths come from `.env` or container defaults.

For a clean environment, build the image and run its smoke check:

```bash
docker build -f docker/Dockerfile -t agcws:dev .
docker run --rm agcws:dev bash scripts/container_smoke.sh
```

## Designs

OpenTitan AES (register/data) is runnable. The verilog-axi `axi_dma` adapter
(descriptors) has deterministic read/write channel harnesses and a
workload-driven runtime path; coupled source-to-destination copying and
top-level DMA power evaluation remain in progress. Ibex (instruction stream)
currently provides its pure legality contract while its simulator harness is a
later bring-up slice.

## Reproducibility

The pinned CHIA commit and tool/model provenance are recorded in results and `docs/DECISIONS.md`. Large waveform artifacts are ignored.

Verification is available locally through the Python contract suite, Makefile
smoke targets, and Docker build/smoke test. GitHub Actions is intentionally not
used. The container includes the open EDA flow and copied Liberty inputs; cloud
credentials and optional LLM integrations are exercised only in experiments.

To verify that an evaluation still matches its recorded inputs:

```bash
make verify-artifact AGCWS_ARTIFACT=out/aes-evaluation
```

This checks the validity/useful-work contract and every recorded input hash.

## License

BSD 3-Clause, matching CHIA.
