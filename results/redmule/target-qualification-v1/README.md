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
