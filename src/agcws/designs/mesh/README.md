# Matched mapped preparation

`python3 -m agcws.designs.mesh.gls synthesize --out SYNTHESIS` writes
`mapped.v`, `manifest.json`, the synthesis recipe, statistics, and logs.
Configure Yosys and its ABI-compatible Slang plugin with `AGCWS_YOSYS` and
`AGCWS_SLANG_PLUGIN`; an empty plugin setting requires built-in `read_slang`.
The configured `AGCWS_LIBERTY` is recorded and checked on replay.

Replay uses the existing traffic generator and packet scoreboard:

```sh
python3 -m agcws.designs.mesh.gls replay --synthesis SYNTHESIS \
  --workload WORKLOAD.json --rtl-waveform RTL/activity.vcd --out GLS --jobs 2
```

The workload is an elaborated packet list, as consumed by `mesh.simulate`.
The RTL waveform must have sibling `program.txt`, `functional.json`, and
`provenance.json` from a matching fresh RTL replay. Source hashes, packet
program, sink pacing, completion, reset count, and window contract are checked.
Frozen attempts are accepted only through the shared verified runtime bridge
layout (`scratch/cache/<id>/attempt-NNN`). `mesh.frozen` verifies the bridge
request/result hashes, original study manifest, complete runtime source inventory,
original provenance, elaborated workload, and rates recomputed from the actual
waveform. Sink pacing is recovered from that verified workload.

The explicit `migration.json` proves that removing exactly four preprocessor
guard lines from the current harness reproduces the entire frozen harness byte
for byte. DUT logic and traffic-driver bytes cannot change under this rule.
All remaining synthesis dependencies must match the original source hashes.
This does not replace or weaken the frozen measurement identity; missing bridge
receipts or any other harness change are rejected.

Set `AGCWS_SKY130_CELL_MODELS` and `AGCWS_SKY130_PRIMITIVES` to real Sky130
functional models. Verilator 5.048 supports their UDP tables; 5.032 does not.
Simulation has zero cell delay and no SDF. Only internal netlist wire names
are shortened to avoid a Verilator trace-name bug; ports and mapped-cell
instances are preserved. No primitive is stubbed.
GLS enables `--trace-underscore` so mapped nets and cell instances remain
visible for OpenSTA activity annotation.

Python interfaces are `synthesize(out)` and
`replay(synthesis, workload_path, rtl_waveform, out, jobs=2)`; callers create
fresh absolute output directories. CLI output directories must not exist.
The shared dispatcher uses `replay_trial(rtl, synthesis, out)`, which creates
its output directory, reads `rtl/workload.json`, and returns `waveform`,
`rtl_waveform`, `clock`, `rtl_clock`, `scope`, `clock_edges`, `bounds`, and
`expected_period_s`. It retains the same strict receipt checks.
Failures retain logs and `failure.json`; successful replay additionally writes
`functional.json`, `activity.json`, `grids.json`, and `provenance.json`.

For shared `windows.evaluate`, pass clock `clk_i`, scope `mesh_temporal/dut`,
expected edges `8200`, expected period `1e-8` seconds, and no marker bounds.
The full window includes eight reset cycles and 8192 traffic cycles. Eight bins
contain 1025 rising edges each. Actual waveform bounds and timestamps are
compared and recorded, rather than borrowed from another design. The synthesis
top is `agcws_mesh`. The harness clock is `mesh_temporal.clk`.

The opt-in CPU integration test is
`tests/integration/test_mesh_mapped_integration.py`. Set
`AGCWS_MESH_INTEGRATION_OUT` to a fresh directory and optionally
`AGCWS_MESH_SYNTHESIS` to an existing verified synthesis directory. It checks
256 packets spanning all routes and multiple bins, then confirms a real mapped
late-traffic replay fails with `MESH_INCOMPLETE`. It needs no API service.

Completed measurements are indexed in [Mesh results](../../../../results/mesh/).
See [Results](../../../../docs/RESULTS.md) for the final comparison.
