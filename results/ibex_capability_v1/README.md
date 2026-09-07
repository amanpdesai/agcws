# Ibex capability v1 — complete development probe

Twelve fixed historical contexts; four model/thinking arms plus two CPU controls.
72 next-batch cells and 144 requested proposals, including 48 model calls. This
is conditional proposal-quality development, not a full search or held-out study.

The manifest, source snapshots, histories, identical per-context payloads and
serving schema were frozen at `0c5d1779` before requests. Both model endpoints
accepted the first context at both thinking settings. All 72 cells are complete.
Pro-4096 has the largest mean next-batch gain (0.14234 versus random 0.02674),
24/24 valid proposals and four newly solved contexts. Total model spend is
estimated at $2.0606266. This is not a held-out or full-search win.

See [results and limitations](../../docs/IBEX_CAPABILITY_V1_RESULTS.md),
[the protocol](../../docs/IBEX_CAPABILITY_V1_PROTOCOL.md) and
[research roadmap](../../docs/RESEARCH_DIRECTIONS.md).

`cells/` preserves every response and charged slot; `parent_histories/` contains
the original histories; `evaluations/` preserves compact CPU evidence without
waveforms. `aggregate.json` contains all-arm metrics, paired descriptive contrasts
and the predeclared screen. `sha256.json` indexes the archive.

```bash
python -m analysis.ibex_capability_v1 --archive results/ibex_capability_v1
```
