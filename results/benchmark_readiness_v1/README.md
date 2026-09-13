# Five-design bring-up evidence (incomplete)

This directory records engineering gates, not a comparative study or a qualified
target bank. See `docs/BENCHMARK_SUITE.md` for all remaining acceptance gates.

- `mesh2/`, `mesh3/`: upstream all-to-all reference success logs and invocation/
  source hashes, using Verilator 5.032 in the prior immutable container.
  `functional.json` independently checks exactly one delivery from every source
  to every destination (16 and 81 packets respectively), not merely process exit.
- `aes/`: four reference-checked, 64-block schedule replays, each exactly 6,774
  clock edges. Compact repeat and explicit expansion have identical activity;
  two random schedules produce distinct eight-bin vectors. This is a fixed-window
  representation gate, not a qualified target bank. Invocation records the
  explicit tool override required by the image used for this check.
- `redmule/`: upstream seeded 4x4 FP16 GEMM reference success (16 output elements,
  zero bit-pattern comparison errors), resolved transitive revisions, software
  compilation and input/binary hashes. Verilator 5.048, no unsupported blackboxes
  or mixed-assignment suppression. `reference.json` identifies the exact image.

The RedMulE test is processor-driven and ends on completion. It is not yet our
fixed-window accelerator-only activity measurement. The dependency checkout and
generated software reside in ignored scratch; this partial bundle alone is not
a complete reproduction package. Neither new DUT is yet a shared-runner backend.
No target is qualified and no Flash call has been made in this bring-up slice.

`mesh_temporal/` records the four-router fixed-window measurement gate: three
different packet release schedules plus an exact repeated replay, each delivering
256 checked packets over 8,200 clock edges. A deliberate horizon violation is
retained as a negative case with no score. The compressed bundle includes input
packets, per-cycle counts, source hashes and functional logs; the summary exposes
the vectors. These are reference profiles, not the eight qualified benchmark
targets, and the compact traffic API/shared-runner mesh port remains outstanding.

## Shared schedule pipeline

`aes/shared_panel.json.gz` and `dma/shared_panel.json.gz` retain the compact JSON
records from source commit `bb9d46d7e`: two classical cells per design, eight
slots each, run concurrently and resumed without changing any cached measurement.
Each bundle maps original relative paths to their JSON text. Sidecar summaries
record the compressed checksum and explicitly label the unqualified plumbing
target. No VCD, executable, compiler output or provider credential is included.
`tests/test_schedule_evidence.py` recomputes every eight-bin profile from the
retained per-cycle counts, target loss, proposal accounting, parent visibility
and summary. That audit is arithmetic/accounting verification, not independent
RTL resimulation. Full waveforms remain in ignored scratch.
