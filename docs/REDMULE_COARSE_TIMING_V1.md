# Coarse release-coordinate qualification

V4's largest release edit was 256 cycles, versus 8192 cycles per observation bin.
The operand-only diagnostic added no qualifications. Before revising any target,
test whole-bin and fractional-bin release moves with the same native language.

Replay all eighteen v4 best programs exactly. For each unresolved request,
enumerate every phase's start plus/minus 8192, 4096, 2048 and 1024 cycles.
Evaluate the full round, retaining invalid/out-of-bounds programs as charged
rejections; do not clip or repair them. Select the lowest valid error among the
parent and the round, retaining the parent on ties. Repeat at most four rounds,
stopping only at a round boundary after qualification. Eighteen parallel
evaluations within each round. Keep global matrix size, operands, job counts,
durations, target vectors, normalization, useful-work gate and tolerance fixed.

This is target-informed witness construction, not a baseline comparison. Archive
every round and parent choice. Passing admits feasibility only after independent
compact-evidence checks; failing does not prove infeasibility. Freeze this rule
before running. No paid calls or automatic additional rounds.
