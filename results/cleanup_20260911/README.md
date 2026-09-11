# Retention receipt

`complete.json` records the exact cleanup scope and selected finalist/witness
cache identities. Compressed plan, deletion journal and log-object index retain
the path and checksum audit trail. No scientific record was modified.

2,911 nonfinalist waveforms were deleted using exact-path `find -delete`.
2,911 large raw execution logs were replaced by SHA-256-verified Zstandard
objects under the local `out/trace-objects/sha256` store. Those cold objects are
not uploaded to Git. All 60 protected caches remain, covering the 36 cell
finalists and 24 construction witnesses.

To restore a log on this machine, decompress `logs.json.gz` to a new index path
and use `python -m maintenance.trace_store restore --index INDEX --path PATH
--destination NEW_PATH`. The index records original bytes, object paths and
checksums. Deleted nonfinalist waveforms require replay; they were not backed
up. Programs, binary, compact measurements and all finalist/witness waveforms
were retained. See the explicit one-off procedure in `archive/cleanup_nonflat.py`.
