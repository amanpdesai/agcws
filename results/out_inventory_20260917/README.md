# Exact output-retention inventory — 2026-09-17

This is a read-only inventory, not a deletion log. The user had already removed
the two previously verified RedMulE long-window witness directories before this
inventory. This pass deletes nothing and does not alter frozen experiment inputs.

- [remove.txt](remove.txt): exact repository-relative top-level paths cleared for
  removal, subject to the recovery tradeoff below. No globs or inferred siblings.
- [keep.txt](keep.txt): every other top-level entry present at inspection. Includes
  essential dependencies **and unverified items**; this is not a claim that all
  these entries must be kept permanently.
- [inventory.json](inventory.json): decision, reason, allocated size where known,
  checked archive identity, matching-record counts, and coverage gaps per path.

The sets are exhaustive and disjoint for the inspected top-level entries.
New paths created later are not cleared for deletion. Sizes are a live snapshot,
not a frozen accounting total: the baseline panel may still be writing.

## What removing an archived run means

Each cleared nonempty directory has a checked packed archive in `results/`.
All archive members pass stored checksums; matching local records were compared
byte-for-byte; the original manifest matches. Local JSON and assembly records
outside generated compilation/toolchain caches must be covered. Symlink trees
are not cleared. Empty directories are separately labeled.

**Waveforms, compiled binaries, generated inputs and unarchived diagnostic logs
are discarded.** Compact research evidence is preserved, but raw trace inspection
requires regeneration. This is not a lossless backup of the entire directory.
Do not remove the corresponding `results/` archives.

The checked candidates are completed historical runs or restored review copies,
not the current `baselines-model-v1` run. Inspection found the active evaluator
processes/container output mounts under the current Ibex panel. No selected
historical run root appeared in maintained `src/`, `scripts/`, `Makefile` or
`.env.example` path references. Recheck activity if deletion is delayed or new
jobs have been launched.

## Mandatory keeps

`baselines-model-v1`, `phase-ga-robustness-v1`, `redmule-dependencies-v2`, `tools`,
`.cache`, `.maintenance`, `trace-objects`, `retired-baselines-maxbin-v1`,
`baselines-maxbin-v1`, and `gemini3-migration-smoke-v1` are deliberately protected.
These contain active/unpublished evidence, referenced tools, retained waveform
objects, recovery indexes, or unarchived provider responses.

The remaining keep decisions fail closed: archive location absent/unverified,
manifest differences, extra compact records, or no completed dependency review.
For example, the `redmule-long-bin-witness-v1` tree has an additional local
`qualification-audit-v2.json` not inside the checked packed archive. A separately
stored copy may permit clearance later, but was not assumed equivalent here.

## Reproduce without deleting anything

```sh
.venv/bin/python -m maintenance.inventory_out --output /tmp/agcws-out-inventory
```

The inventory command writes only its requested report directory and prints
verification results. It contains no deletion implementation.
