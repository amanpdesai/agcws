# Strong-model matched panel — prepared, not launched

**Superseded before launch.** The ten-call v1 smoke produced eight MAX_TOKENS
responses at the 8192-token ceiling. Do not execute this panel. All original
manifests are retained; see `strong_smoke_v1_plan/outcome.json` for the failure.

Model: `gemini-3.8-flash`, MEDIUM thinking, arm `strong-medium`.
Five designs, nine profiles, ten matched seeds: 450 cells.

[Replacement protocol](../../docs/STRONG_MATCHED_V2.md).
[preparation.json](preparation.json) records the source/runtime/schema bridge,
all fifty design/seed shared-initialization checks and model settings. Each design
contains `config.json`, `manifest.json` and a hash-pinned `launch-contract.json`.
CPU and Flash-Lite results are reused, not rerun.

Full execution is deliberately stopped pending user authorization. Caps are
$120/design, $600 total, and can pause work; they are not a cloud balance.
