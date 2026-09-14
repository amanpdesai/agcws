# AES arithmetic-feedback smoke v5

Seed 8503, eighteen targets, three arms, sixteen charged slots per cell.
864 slots; 126 Flash calls; $1.8558573 known cost; no API errors or unknown
usage. Strict and operational feedback checks pass 18/18.

Excluding shared initialization, 140/252 generated candidates are valid.
This is engineering readiness, not comparative inference. One successful
request took 223.5 seconds with the corrected 600-second deadline.

The packed archive restored 3,552 compact files with exact byte verification.
`audit.json`, raw responses, trials and measurements are inside. The parent
config and qualification receipt are retained separately as gzip files.
Restore with `python maintenance/archive_study.py restore --source
results/aes/bank-smoke-v5 --destination <new-directory>`.

See [the authoritative results](../../../RESULTS.md).
