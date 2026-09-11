# Finalist validation

Current findings are in [RESULTS.md](../RESULTS.md). Historical `analysis.*`
audit/report commands below run from the [isolated source archive](../archive/README.md).
Individual `validation.*` measurement stages remain maintained in this checkout.

## Native eight-window measurements

The completed panel is in `results/windowed_power_v1/`. Use
`python -m analysis.audit_windowed_archive` for compact review without tools.
The frozen search scripts retain their full-window behavior; this separate
versioned validation layer supplies native `-begin_time` / `-end_time` bounds.

For a new measurement directory and already matched waveforms:

```bash
.venv/bin/python -m validation.window_power \
  --waveform <GLS-VCD> --rtl-waveform <matched-RTL-VCD> \
  --synthesis <mapped-directory> --clock clk_i --scope aes_core_smoke/dut \
  --expected-edges 6774 --out <new-directory>
```

DMA uses `--clock clk --scope axi_dma --expected-edges 12000`. Tools and Liberty
come from the existing `.env` configuration. This v1 measurement contract uses
a 10 ns clock and exactly eight bins, not arbitrary clock frequencies or goals.
`validation.window_matrix` runs the declared selection with bounded workers;
its defaults resolve the recorded experiment roots, not new workloads. It
refuses existing output directories. `validation.reference_power` replays each
original achieved reference and verifies its lowering and functional record.
Reference GLS needs the cell-model environment paths described below.

See `docs/WINDOWED_POWER_PROTOCOL.md` for event-free cuts, carried-in state,
leaf-sum precision checks and reference-only normalization. Independent native
semantics tests can be repeated with:

```bash
.venv/bin/python -m validation.check_window_semantics \
  --source <pinned-OpenSTA-source> --out <new-directory>
```

## Matched replay tier

This directory is separate from the frozen search implementation. Its programs
record their own input hashes and do not modify workload generators, policies,
validators or RTL. A completed activity search is not a validated power result.

`python -m validation.aes_gls synthesize --out <new-directory>` requires
`AGCWS_SLANG_PLUGIN` compatible with `AGCWS_YOSYS`. It synthesizes unmasked AES
with the LUT S-box and 32-bit entropy interface, matching the RTL transaction
harness. The parameter manifest and 128-bit state-port check prevent accidental
reuse of the older masked, two-share netlist.

`python -m validation.aes_gls replay --synthesis <directory> --workload <json>
--clock-edges <expected> --out <new-directory>` requires
`AGCWS_SKY130_CELL_MODELS` and `AGCWS_SKY130_PRIMITIVES`. `AGCWS_IVERILOG` and
`AGCWS_VVP` optionally override executable lookup. The workload is the lowered
AES transaction DSL, not the structural schedule. The existing transaction
compiler and shared SV driver preserve operation order, idle placement,
reference ciphertext checks and reset/acknowledgement timing. Compilation is
content-addressed; the replay must match the supplied observation horizon.

This is functional, zero-delay gate simulation. It does not measure glitches
from timing delays or constitute signoff power. OpenSTA evaluation and matched
window/annotation audits remain separate validation steps.

`python -m validation.dma_gls --rtl <completed-evaluation-directory>
--synthesis <mapped-directory> --out <new-directory>` replays the original
DMA workload through `axi_dma_pipelined_tb`. It preserves the observation
horizon and trailing idle cycles, disables the legacy diagnostic bypass,
and requires the entire completion/timing observation record to equal RTL.
The same Sky130 model environment variables are required. No new wall-clock
deadline is imposed; the existing semantic observation horizon still applies.

`python -m validation.structural_case --runs <held-out-run-root> --freeze
<freeze.json> --design aes|dma --target <reference> --policy <frozen-policy>
--synthesis <mapped-directory> --out <validation-root>` validates the fixed
seed-400 finalist from one completed cell. It audits the cell and frozen source
hashes, checks that the raw RTL workload/vector matches the selected trial,
and runs GLS plus OpenSTA. A content-identical completed replay may be reused;
changed validation inputs fail rather than silently reusing stale evidence.
Do not launch concurrent cases with the same replay identity.

Individual replays may overlap the frozen search. Final reporting still requires
the complete held-out audit, `analysis.select_structural_finalists`, and
`analysis.archive_structural_finalists`. The latter independently reselects all
16 cases from the held-out archive, verifies replay artifacts, and compares
each waveform's own timescale and start/end timestamps. Keep raw waveforms until
that reconciliation succeeds. Full-window power remains distinct from temporal
power-shape validation.

The Dockerfile retains the Sky130 functional models from its pinned OpenSTA
source and sets the two model paths inside the image. At OpenSTA commit
`c821ad1ad07031de831fd567fc626bf70d522c49`, these files are byte-identical
to the host models used for the matched validation:

| File | SHA-256 |
|---|---|
| `sky130_hd.v` | `5ff4558207faf8ea0d4f35ea6d85e1ff36f57936d307423c8f234204398d1c3a` |
| `sky130_hd_primitives.v` | `81351b44f54dd9b5e3cd07a845cbe9d90e889d29edfcbff57a527280839bbccc` |

This source check does not imply that host experiments ran inside Docker or that
the updated image has completed a full validation replay.
The 2026-09-06 Python-3.10 container smoke was blocked before Python started
(`exec /usr/local/bin/python: operation not permitted`); no successful image
replay is claimed. Streaming-hash tests pass on the host without using
Python 3.11's `hashlib.file_digest` API.
