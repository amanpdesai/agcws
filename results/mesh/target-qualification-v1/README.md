# Mesh target qualification v1

CPU-only witness search: nine requests (eight non-flat families plus one control),
phase-random and phase-GA, 256 proposals per policy/request, one seed per split.
Requested vectors and failed admissions are retained in the
[frozen request bank](../../benchmark_targets_v1/mesh-temporal/requested_bank.json).

| Split | Seed | Completed slots | Qualified non-flat | Control | Qualification report | Archive |
|---|---|---|---|---|---|---|
| Development | 7300 | 4608 | 6/8 | 1/1 | [report](../../benchmark_targets_v1/mesh-temporal/development-qualification.json) | [bounded shards](development/) |
| Confirmation | 7400 | 4608 | 5/8 | 1/1 | [report](../../benchmark_targets_v1/mesh-temporal/confirmation-qualification.json) | [bounded shards](confirmation/) |

Each archive is byte-restoration verified and includes invalid attempts. Shards
are bounded at 32 MiB; the existing checksum manifest and restore command support
multiple shards. This is not eight-profile readiness, a model comparison or gate
power evidence. Witness programs must not enter agent payloads.
