# Retention pass — 2026-09-09

Removed 4,016 completed Ibex depth **non-finalist waveform files**, reclaiming
70,444,781,568 allocated bytes (65.6 GiB). All 48 selected finalist traces,
simulator binaries, programs, logs and measurements remain. The full depth
archive passed its independent audit before deletion; all 61,081 archived
file hashes and the retained trace fingerprints were checked afterward.

Deletion used a revalidated, exact-file GNU `find -delete` list, not a directory
wildcard. The compressed plan and deletion journal here are the audit trail.
Deleted traces have no trash copy; regeneration requires the retained programs
and pinned runtime. These archives are tracked in Git; heavy inputs remain local.

The project/owner-scoped Docker prune reclaimed a reported 924.3 MB. No named
volume, shared builder, running container or tagged image was selected. Deleted
layers can require rebuilding/pulling; current pinned runtime checks must still
pass before any new experiment.

## Permission-blocked remainder

16,000 stale traces under exactly `out/ibex-full` and
`out/aes-baseline-matrix-docker-seed1` occupy 505,584,082,944 allocated bytes
(470.9 GiB). Every parent directory is non-writable by this account.
`sudo -n true` reports that a password is required. No ownership bypass or
privileged-container deletion was attempted.

From `/home/aman/agcws`, the owner can review and authorize the retained plan:

```bash
.venv/bin/python -m maintenance.find_delete --plan out/.maintenance/root-owned-traces-20260909.json
sudo .venv/bin/python -m maintenance.find_delete --plan out/.maintenance/root-owned-traces-20260909.json --apply
```

The command rechecks file identity, active references, tracked status and exact
targets before deleting. It does not remove non-waveform evidence or directories.
Do not replace it with a broad recursive deletion. The gzip plan here is a
backup of the reviewed local plan, not evidence that its deletion occurred.

This pass frees disk, not application RAM. At inspection the host had about
1.2 TiB available memory; no process was killed and no kernel cache was dropped.
