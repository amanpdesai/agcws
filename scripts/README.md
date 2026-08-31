# Reproducibility scripts

Scripts in this directory are small, inspectable entry points used by local
and container tasks. They must not embed machine-specific EDA paths; use the
repository `.env` settings or command-line arguments.

```bash
python scripts/inspect_liberty.py "$AGCWS_LIBERTY"
python scripts/aes_sources.py
```

The AES source manifest is intentionally separate from the future TileLink
harness. OpenTitan's `aes` top level depends on common OpenTitan primitive and
TileLink packages; those dependencies must be added explicitly when the
harness compile command is implemented.
