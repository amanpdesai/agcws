# RedMulE target qualification v1

CPU-only witness search: nine requests (eight non-flat families plus one control),
phase-random and phase-GA, 256 proposals per policy/request, one seed per split.
Each split completed 4608 slots; all failed attempts are retained.
Development qualifies 0/8 non-flat requests and confirmation 1/8. Both controls
qualify. The confirmed non-flat request is quiet-interval; this bank is not ready.

| Split | Seed | Qualification report | Archive |
|---|---|---|---|
| Development | 7300 | [report](../../benchmark_targets_v1/redmule-temporal/development-qualification.json) | [bounded shards](development/) |
| Confirmation | 7400 | [report](../../benchmark_targets_v1/redmule-temporal/confirmation-qualification.json) | [bounded shards](confirmation/) |

Each archive was restored and compared byte-for-byte with the exported source
files before publication: 19,763 files for development and 19,426 for confirmation.
Shards are bounded at 32 MiB and checksummed in `evidence.pack.json.gz`.
Raw scratch remains unchanged. A completed search is not target qualification:
the reports retain unsuccessful requests, and this is not full-study readiness
or gate-power evidence. Witness programs must not enter agent payloads.

## Existing-trace timing audit

[Development](development-timing.json) and [confirmation](confirmation-timing.json)
group unique valid workloads by size/pattern, retaining invalid proposal counts.
These are search-selected samples, not representative latency benchmarks.
Completion timestamps include software/reference overhead; actual hardware start
times are not recorded. Bin crossings therefore diagnose release/completion
misalignment, not accelerator latency or proof of infeasibility.

Reproduce after restoring either split's archive to an empty directory:

```sh
.venv/bin/python analysis/redmule_timing.py --directory RESTORED_SPLIT --output NEW_REPORT.json
```

The audit checks executed programs, reference work, ordered completion records
and total proposal counts. It deduplicates cache hits and hashes consumed evidence.
Both reports were independently regenerated from restored per-design archives;
the resulting JSON objects, including evidence digests, matched the reports here.
