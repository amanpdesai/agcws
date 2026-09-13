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
