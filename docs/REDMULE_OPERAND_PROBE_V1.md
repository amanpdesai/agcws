# RedMulE operand witness probe v1

The completed v4 timing refinement leaves seven requests unqualified. Before
changing targets or the observation window, test an unused workload dimension:
matrix operand patterns and seeds. This is an explicitly target-guided CPU
qualification extension, not a policy comparison or held-out inference.

Freeze each v4 best program's matrix size and entire phase schedule. Replay all
18 parents, and for each of the seven misses evaluate the Cartesian product of
three existing patterns (`zeros`, `alternating`, `random`) and seeds 0–15.
All 354 slots count, including duplicates. No early stopping, additional seeds,
fallback program or tolerance adjustment is allowed. Use 18 concurrent workers.

Check parent replays against their original validity, rates and full profiles
before interpreting variant errors. The refreshed source inventory is recorded;
this pass alone does not refresh the calibration or admit a full-study bank.
Keep every failed attempt. Selecting the minimum valid error per request answers
only witnessed feasibility. Functional correctness and useful-work gates remain
unchanged. If no variant qualifies, report the miss without substituting a shape.
