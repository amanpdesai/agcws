# DMA arithmetic-feedback smoke v5 — strict failure retained

Seed 8503, eighteen targets, three arms, sixteen slots per cell. 864 slots;
126 Flash calls; $1.7402685 known cost; no API errors or unknown usage.
Strict and operational checks within this smoke pass **17/18**, not eighteen.
Development quiet-interval produces its only valid generated candidate in the
final batch, without a subsequent feedback call. Overall generated validity
excluding initialization is 141/252.

The separate [delivery diagnostic](../late-feedback-v1/README.md) does not
rewrite this outcome. The packed archive restored 3,362 compact files with
exact byte verification; audit, calls, trials and measurements remain intact.
Parent config and qualification receipts are retained separately as gzip.
Restore with `python maintenance/archive_study.py restore --source
results/dma/bank-smoke-v5 --destination <new-directory>`.

See [the authoritative results](../../../RESULTS.md).
