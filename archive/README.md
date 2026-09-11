# Historical research archive

The maintained pipeline lives in `src/agcws/pipeline/`; findings live in
`RESULTS.md`. Historical runners are not imported by active code.

`legacy-source.tar.gz` preserves the exact pre-consolidation source tree,
protocols, reports and tests at the commit recorded in `manifest.json`.
Every member is hashed. Raw study evidence stays in `results/`, not in this
source archive. No credentials, scratch waveforms or third-party clones are
included. Older studies additionally retain their original source commits and
manifest hashes; consolidation does not rewrite those identities.

Use `python -m agcws.pipeline archive-check` to verify the snapshot, or
`python -m agcws.pipeline archive-extract --destination /absolute/new/directory`
to reconstruct it. Extraction refuses an existing destination, unsafe paths,
and links. The original `experiments/`, `analysis/`, `scripts/`, `tests/`,
`docs/`, package sources and Makefile reappear only in that isolated directory.
Read the original protocols and reports there with their original relative
links. Reattach the matching read-only third-party dependencies and result
archives when auditing, or use `archive-audit` for the completed non-flat study.

No automatic historical runs are performed by extraction or verification.
`archive-audit` runs only the frozen compact-evidence audit, never simulation
or a model call. Historical tests are preserved rather than silently rewritten
to pretend they tested the consolidated implementation.
