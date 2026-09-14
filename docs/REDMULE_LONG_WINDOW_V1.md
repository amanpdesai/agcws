# RedMulE longer-window diagnostic v1

Authorized 2026-09-14, before new measurements. This is a new measurement
version, not a repair to the frozen 65,536-cycle bank. That bank and its
operand/coarse-timing qualification failures remain evidence.

## Fixed intervention

Use domain `redmule-temporal-long`: 262,144 clock edges, eight equal
32,768-edge bins. Keep the 4x4 RTL, FP16 reference checks, scope, 1,024-MAC
useful-work floor, matrix sizes, data patterns, sequential job semantics,
128-job cap and 32-phase cap unchanged. Every requested job must finish.
The original domain retains its 65,536-edge contract.

The hypothesis is that more jobs fit within each bin, reducing the coarse
pulse quantization of short-window activity. This does not prove that any
particular request becomes feasible. Do not change the horizon again in
response to these results without another explicit protocol version.

## Calibration and qualification

Fresh 64-proposal calibration: seeds 7200 and 7201, 32 random proposals each,
including every rejection. The random generator keeps its uniform 1..8 phase
count, size and pattern choices. It preserves a 2,000-cycle initial offset
and 9,536-cycle final drain reserve; the release interval expands with the
window. Its total initial job sampling upper bound scales from 12 to 48,
preserving approximate offered load rather than diluting activity fourfold.
These changes are frozen before measuring the new corpus.

Use the existing calibration report's 5th/95th percentile bounds and existing
v1 analytic target generator. Generate both development and confirmation
banks: eight nonflat shapes and a separate flat control each. Use the existing
qualification procedure, phase-random and phase-GA, 256 slots per arm/request,
seeds 7300/7400, and retain all unsuccessful requests. Tolerance remains 0.1;
the nonflat constant-vector floor must exceed 0.12. Qualification is measured,
never inferred from a model or from a successful short-window parent.

This is CPU-only work. No full Flash or Pro run is authorized by this test.
Any later smoke must use the admitted longer-window bank and matching runtime.

## Provenance and promotion

Record an independent manifest, calibration, request bank and qualification
archive under the RedMulE design. Never overwrite the short-window artifacts.
Current source inventory hashes all Python modules, so this change also alters
the global runtime fingerprint: existing other-design evidence stays valid for
its recorded revision, but cannot silently become current-runtime evidence.
Readiness requires explicit replay/compatibility evidence before promotion.
