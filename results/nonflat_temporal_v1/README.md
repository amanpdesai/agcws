# Non-flat temporal confirmation evidence

Complete: 36 trajectories / 4,608 slots. Findings and limitations live only in
[RESULTS.md](../../RESULTS.md).

`manifest.json`, `witnesses.json`, `targets.json` and `search_manifest.json`
retain frozen inputs and witness selection. `panel/` contains compressed
proposals, responses and trials; `evaluations/` contains compact measurements.
`summary.json` is the complete-panel audit output; `cost_summary.json` retains
known usage and unknown-call reservations. `complete.json` records completion.
Launch records describe historical execution, not current status.

Run `make archive-audit` from the root to verify this evidence using its exact
historical code. The original protocol and runner are in the
[source archive](../../archive/README.md). No new experiment is required.
Waveforms and simulator binaries are not included in this compact archive.
