# CPU witness-search evidence v1

Completed ordinary pipeline exports, packed and restoration-verified by
`maintenance/archive_study.py`. Requests and selection procedure are frozen in
`results/benchmark_targets_v1/` and `docs/TARGET_QUALIFICATION_V1.md`.

Mesh development and confirmation each contain nine requests, two CPU policies,
one seed per split and 256 proposed slots per policy/request. All 4608 slots per
split completed, including invalid proposals. These are feasibility searches,
not held-out claims about policy superiority. Qualification is recomputed by
`analysis/target_qualification.py`; requested vectors are never replaced by
achieved profiles. Do not include witness programs in any model payload.
