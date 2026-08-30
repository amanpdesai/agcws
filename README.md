# Agentic Goal-Conditioned Workload Synthesis

Given RTL, a legal stimulus interface, and a target dynamic-power profile, an agent synthesizes semantically valid workloads toward that behavior. Targets may be scalar, compositional, or coarse temporal.

Built as a composable [CHIA](https://github.com/ucb-bar/chia) loop for the A³ CHIA Hackathon (MICRO 2026).

## Status

Under active development (2026-08-29 → 2026-09-20). Not yet usable.

See `docs/ARCHITECTURE.md` and `docs/PLAN.md`.

## Designs

OpenTitan AES (register/data), verilog-axi `axi_dma` (descriptors), and Ibex (instruction stream).

## Reproducibility

The pinned CHIA commit and tool/model provenance are recorded in results and `docs/DECISIONS.md`. Large waveform artifacts are ignored.

## License

BSD 3-Clause, matching CHIA.
