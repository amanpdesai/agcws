# Finalist validation

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
