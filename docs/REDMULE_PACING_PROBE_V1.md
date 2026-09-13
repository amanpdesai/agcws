# RedMulE pacing probe v1

Freeze this diagnostic before execution. It is not a new qualification attempt
and cannot change the v1 request bank. No models or targets participate.

The full factorial grid is 3 matrix sizes (4, 8, 16), 3 operand patterns (zeros,
alternating, random), 3 job-count multipliers (1, 2, 4), and 2 pacing modes:
54 predetermined workloads. Data seed is 7500. Minimum jobs is the ceiling of
1024/size³; each multiplier scales that count. Queued jobs all become eligible
at cycle 2048. Paced jobs are evenly released starting at 2048 over 49152 cycles.
Every run uses the unchanged 65536-cycle measurement contract and functional/
useful-work gates. Incomplete jobs invalidate the workload; do not extend its
deadline or score its activity anyway.

Run at most 12 CPU measurements concurrently. Use the shared RedMulE backend,
cache, container, reference checker and fixed-window extraction. The driver pins
its own hash and a verified existing measurement manifest. It has no optimizer,
policy inference or target loss. A run lock prevents duplicate drivers; completed
cases resume without reruns. Infrastructure errors stop completion; known invalid
workloads remain recorded. Retain the entire grid, including failures.

Compare achieved bin rates, completion timestamps and release/completion
alignment across the fixed factors. Do not infer isolated hardware latency:
completion includes controller/reference overhead, and start timestamps are not
instrumented. Size-4 minimum work already requires 16 jobs, so this is not an
isolated single-job latency study. It measures controllability under the actual
useful-work contract. New target endpoints or witness-search budgets require a
separate frozen v2 qualification procedure after this diagnosis.

```sh
.venv/bin/python scripts/probe_redmule_pacing.py prepare --reference out/five-design-calibration-v1-redmule-temporal --directory out/redmule-pacing-probe-v1
.venv/bin/python scripts/probe_redmule_pacing.py run --reference out/five-design-calibration-v1-redmule-temporal --directory out/redmule-pacing-probe-v1 --execute
```

The diagnostic has a distinct manifest/terminal format; do not feed its records
to study AUC, solve-rate or policy-comparison analysis.
