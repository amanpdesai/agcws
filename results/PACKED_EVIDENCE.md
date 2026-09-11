# Packed evidence: verify, inspect, recover

[Migration receipt](packing_20260911.json): 133,140 → 3,160 tracked paths;
130,015 original files preserved. Both the frozen study audit and current
solution inspection regenerate unchanged after loose-copy removal.

Packing changes storage, not scientific records. Twelve studies with more than
500 tracked nested files have their nested trees stored in `evidence-NNN.tar.gz`
shards, capped at approximately 32 MiB of original file content per shard.
Root summaries, targets, manifests and READMEs remain directly readable at their
original paths. No superseded study, simulator output or source snapshot is
discarded. Small studies and windowed-power reports remain loose.

Each `evidence.pack.json.gz` records every original relative path, SHA-256,
size, mode and Git blob identity, plus the shard hashes and pre-cleanup commit.
The original frozen manifests are unchanged. The format is tar rather than
JSONL because evidence includes exact gzip bytes, assembly and logs, not just
JSON records. SHA-256/member/mode checks precede acceptance of restored files.
Extraction rejects traversal, duplicate members, links and unexpected entries.

## Commands

```bash
PYTHONPATH=src .venv/bin/python -m agcws.pipeline evidence-check
PYTHONPATH=src .venv/bin/python -m agcws.pipeline evidence-extract \
  --study nonflat_temporal_v1 --destination /tmp/agcws-review
make archive-audit
```

Choose a destination that does not exist. Repeat `--study` for multiple studies.
The review workspace restores chosen nested evidence at its original
`results/<study>/...` paths. Other files and source directories are symlinks to
this checkout: **treat those as read-only**. It is a local review view, not a
self-contained export. Shards also work with ordinary tar tools, but the Python
entry point performs the full checks.

The historical `archive-audit` command automatically creates a temporary review
view for the non-flat study and runs the original isolated audit. It compares
the regenerated summary to the unchanged published one and launches no model
call or simulation. Other historical readers should run from an isolated source
snapshot with this restored results view, following [archive instructions](../archive/README.md).

To run current solution inspection against restored evidence:

```bash
cd /tmp/agcws-review
PYTHONPATH=src .venv/bin/python -m analysis.solution_inspect --out /tmp/review-inspection.json
```

Do not edit frozen manifests or source hashes to accommodate relocation. Old
links to individual nested files describe paths in the restored view; use the
[evidence index](README.md) to reach directly readable study summaries first.
Pre-cleanup loose files also remain in Git history, without a history rewrite.
Consequently this improves checkout file count and navigation; it does **not**
promise a smaller full-history clone or removal of old Git objects.

## Maintenance boundaries

`maintenance/pack_evidence.py` is the one-time migration tool. It accepts only
tracked regular files matching their Git-index bytes. Packing verifies a full
round trip before loose copies can be retired. The separate retirement operation
rechecks every shard and original file, then uses GNU `find -files0-from` with
exact validated paths and `-delete`. No broad recursive deletion is used.

No runtime packages, submodules, prompts or frozen protocols were moved. A future
structural cleanup must preserve imports and resource paths and has its own test
gate. Fewer packages are not an objective in themselves.
