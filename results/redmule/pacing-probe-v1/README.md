# Fixed pacing diagnostic v1

All 54 predeclared CPU cases completed: 48 valid; six useful-work rejections.
Every rejection requested 64 size-4 jobs, exceeding what completed in the fixed
window. Failures remain in the byte-restoration-verified archive (472 files).
Re-running the driver reused completed checkpoints; it launched no new replay.

The [frozen procedure](../../../docs/REDMULE_PACING_PROBE_V1.md) varies size,
operand pattern, job count and queued versus paced releases. Size-16 random
operands with four paced jobs produced rates approximately
`[54.4, 4.0, 54.8, 55.3, 4.1, 54.3, 2.0, 2.0]` transitions/edge. The same four
queued jobs produced `[54.4, 55.3, 106.8, 2.8, 2.0, 2.0, 2.0, 2.0]`.
Thus release scheduling changes temporal activity; this does not qualify any
of the eight requested target families or establish gate-power behavior.

Restore with `maintenance/archive_study.py restore`; the archive contains the
fixed manifest, every per-case result, functional records, activity samples and
terminal summary. It is a diagnostic, not a search-policy study.
