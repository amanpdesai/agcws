# Artifact retention

## Verified compressed objects

`python -m maintenance.trace_store pack --plan <plan.json> --index <new-index.json>`
stores traces by SHA256 under `out/trace-objects/sha256/`. Packing preserves
originals. `retire --index <index.json>` independently verifies compressed and
decompressed hashes before exact-path GNU find deletion. `restore --index
<index.json> --path <original-relative-path> --destination <new-file>` restores
bytes without overwriting a different file. Keep both index and objects; this
local store is not an off-host backup.

On 2026-09-06, `structural-population-development-v1` was archived in
`out/.maintenance/structural-development-objects-20260906.json`: 1,903 traces,
4,460,660,036 original bytes, 1,525 unique objects totaling 69,146,827 compressed
bytes. Every object passed decompression verification; two largest traces were
restored and compared with originals before retirement. Exact-path deletion
reclaimed 4,463,837,184 allocated bytes. Frozen held-out and current finalist
waveforms were not retired.

The compact summary, original plans, recovery index and successful deletion
journals are tracked under `results/artifact_retention_20260906*`. Compressed
objects remain local and ignored by Git. Restoring requires `zstd` on PATH.

## Exact-path GNU find deletion

`python -m maintenance.find_delete --plan <existing-plan.json>` revalidates
the original file identities and reports permissions without deleting anything.
Add `--apply` only for a reviewed plan. It uses `find -P -files0-from <NUL-list>
-maxdepth 0 -type f -delete -print0`, so it does not recursively search a broad
directory at deletion time. It rejects active runs, changed paths, symlinks,
tracked files and protected build/evaluation directories. Successful removals
are journaled. It never deletes non-waveform files or directories.

On 2026-09-06, the seven explicitly superseded oracle/projection/replay runs in
`out/.maintenance/superseded-oracle-20260906.json` lost 127 regenerable traces,
reclaiming 4,643,930,112 allocated bytes. Inputs, measurements and provenance
remain. These traces are not recoverable from trash; regeneration is required.
The current 180-report windowed archive still passes audit.

The earlier root-owned remainder was rechecked: all 16,000 identities remain
unchanged, totaling 505,584,082,944 allocated bytes. Passwordless sudo is still
unavailable. No privileged workaround was attempted. From the repo root, an
authorized operator can use the same guarded find implementation:

```bash
sudo /usr/bin/python3 -m maintenance.find_delete \
  --plan out/.maintenance/stale-waveforms-20260905.remaining.json
# After reviewing the dry-run output:
sudo /usr/bin/python3 -m maintenance.find_delete \
  --plan out/.maintenance/stale-waveforms-20260905.remaining.json --apply
```

The broader read-only inventory found about 836 GiB under `out/`, 218 MiB in
`results/`, and 116 MiB in `.git` before this pass. Not all `out/` data is stale:
the completed frozen panels retain large raw waveform sets. Compression and
restoration need a checked index before retiring those paths. Shared Docker
reported 485.1 GB of reclaimable build cache, but this is not project-owned
evidence and is not authorization for global pruning. The project-scoped prune
preview showed no owned stopped containers or dangling images.

Pinned native OpenSTA installation and verification are documented in
`docs/OPENSTA_UPSTREAM.md`. `verify_opensta_windows.py` verifies the source pin,
native window flags and upstream regression without changing `.env` or results.

`results/` is research evidence. `out/` holds scratch outputs and reusable
builds. Container removal does not remove these host files.

Preserve ledgers, workloads, calibration, summaries, activity measurements,
provenance, netlists and Liberty files. Keep active held-out outputs and build
caches. Once a run is retired, its VCD/FST/SAIF traces can be regenerated from
retained workloads and source provenance; they are not kept indefinitely.

```bash
.venv/bin/python maintenance/clean_artifacts.py \
  --plan out/.maintenance/example.json --targets explicit-old-run
# Inspect the plan before deletion:
.venv/bin/python maintenance/clean_artifacts.py \
  --plan out/.maintenance/example.json --apply --retire
```

Planning is read-only and records exact file identities, sizes and timestamps.
Applying rechecks identities, rejects active run references, tracked files,
symlinks, path escapes and protected build/evaluation directories. Deletion
is limited to the enumerated waveform files and has an audit log. `--retire`
moves the remaining directory to `out/retired/`, without deleting evidence.
`--skip-unwritable` emits a separate `.remaining.json` plan and leaves its
directories in place. Never use broad recursive deletion on `out/` or a
shared Docker prune to solve artifact accumulation.

## 2026-09-05 cleanup

Across 36 explicit old runs, 106,853 waveform files (640,764,080,128 allocated
bytes, about 641 GB) were removed and 34 cleaned directories moved under
`out/retired/`. Non-waveform evidence was preserved. These raw traces are not
recoverable from trash; regeneration requires the retained workload and flow.
Active held-out directories and their executable source digests were unchanged.

16,000 remaining root-owned traces occupy 505,584,082,944 allocated bytes
(about 506 GB) in `ibex-full` and `aes-baseline-matrix-docker-seed1`.
Passwordless sudo is unavailable. To finish only the validated remainder:

```bash
sudo /usr/bin/python3 maintenance/clean_artifacts.py \
  --plan out/.maintenance/stale-waveforms-20260905.remaining.json --apply --retire
```

Detailed plans and deletion logs remain in `out/.maintenance/`. A changed
file or active reference causes refusal rather than deleting new work.
Shared Docker inventory was inspected but not globally pruned; future builds
and containers use the project-scoped wrappers in `docker/`.
