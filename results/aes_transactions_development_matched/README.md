# Matched scalar-edit control: completed development panel

All 15 cells are complete: five scalar targets × seeds 100–102, 50 proposal
slots per cell. This is the non-LLM scalar-edit-evolution arm only, not a
complete agent comparison. Independent ledger audit passed all 750 slots.

The control shares random initialization and top-four valid parent selection
with semantic-edits-v4, then makes up to eight schema-bounded scalar edits.
Invalid proposals are retained and charged. No seed here is held-out.

Recompute with:

```sh
.venv/bin/python scripts/audit_semantic_archive.py results/aes_transactions_development_matched
.venv/bin/python scripts/summarize_semantic_development.py results/aes_transactions_development_matched
```

The source commit plus captured source-file hashes identify the working tree
used by each cell. Metadata/analysis files changed during development; this
must not be interpreted as a single frozen held-out study.
