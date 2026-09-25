Matched Ibex GLS
===============

Ibex power estimates are included under `ibex-10ns-estimate-v1`. This policy
retains switching-reconstruction exceptions with per-case diagnostics, while
requiring functional replay, aligned windows, finite power and annotation.
The original integration discrepancy was 0.55784%, not an accuracy bound for
all workloads. See [final results](../../../../docs/RESULTS.md) for coverage.

The frozen original simulator emits `MHPMCounterNum=12`; the local bring-up
build uses zero. Synthesize the frozen configuration with `--mhpm-counter-num 12`.
Replay checks all 25 mapped parameters against the original waveform before
simulation. A zero-counter netlist cannot validate that frozen run.

`python -m agcws.designs.ibex.gls synthesize --closure <simulation.vc> --out <new-dir>`
maps `ibex_top` with the explicit simple-system parameters. Use the pinned
`lowrisc_ibex_ibex_simple_system_0.vc` beside the reference simulator. The driver
uses the existing environment-backed Yosys, Slang and Sky130 Liberty paths.
The Slang plugin must match the Yosys binary ABI.

`python -m agcws.designs.ibex.gls replay --synthesis <mapped-dir> --rtl <checked-run> --out <new-dir>`
uses the existing ELF's checked binary image and original simple-system
bus, RAM, timer and instruction tracer. Set `AGCWS_SKY130_CELL_MODELS` and
`AGCWS_SKY130_PRIMITIVES` to the existing functional models. Verilator builds
with two jobs by default (`--jobs`). Neither operation has an automatic timeout.
Existing output directories are refused. No source runtime or result is edited.

Replay checks the interpreter's eight registers and 64 memory words, every
retired PC/instruction and its relative timing through halt, and all three
retired markers. Original functional input paths and hashes must still match;
the driver does not silently relocate or rewrite frozen measurement identity.
An archived run must first be restored independently with its hashes intact.
For a binary-only frozen artifact, the explicitly supplied `frozen_receipt`
binds the original request, result, simulator hash and exact replay rates. Input
paths are translated through the declared original container mounts and every
hash is checked. The original build `.vc` was not retained, so this binding does
not claim proof that the original binary was built from the current RTL sources.

`receipt.json` is written only after validation. Its `rtl_bounds` and
`gls_bounds` are independent half-open native-tick intervals anchored to
`measure_start`, each exactly 200,000 cycles. `body_complete` must lie strictly
inside and `measure_stop` strictly after the interval. Both native waveforms
use 1 ps ticks and a two-tick period. There are eight 25,000-cycle bins.
`clock` and `rtl_clock` are qualified VCD paths; `sta_scope` omits the synthetic
`TOP` prefix. Shared power integration must use these bounds and verify
`expected_clock_period_s`, rather than count the entire waveform. A tick
immediately before a boundary can contain a falling edge; it is not an
event-free timestamp. Exact finer-resolution recoding must preserve physical
time and carry conversion hashes when merely changing resolution.

The common `replay_trial(rtl, synthesis, out)` adapter deliberately declares a
10 ns physical reference clock for power. It emits separate `power_gls.vcd`
and `power_rtl.vcd` files by exact integer timestamp multiplication by 5000,
keeping 1 ps units. This changes physical duration, not just resolution.
`power_clock.json` records that assumption, both hashes/durations, factor and
scaled bounds. The native files, traces and frozen RTL score are unchanged.
The adapter returns those power waveforms, scaled bounds and
`expected_period_s=1e-8`; it does not report power at the simulator's nominal
two-picosecond period. Clock transitions now have 5000 ticks of separation,
so a tick immediately before a marker boundary is event-free.
The returned `bounds` are GLS bounds and `rtl_bounds` are independent RTL
bounds. An absolute startup offset is allowed; relative retirement timing
must still match exactly.

The harness explicitly asserts reset at tick 1 and releases it at tick 8, so
closed internal clock gates do not prevent reset initialization. An online
scoreboard fails on the first wrong or missed retirement without a runtime timeout.
The successful recipe uses negative-edge sampling of registered
memory responses, with requests and grants connected directly. It also needs
known-input nonblocking equivalents for seven SKY130 UDPs, including the unreset
flip-flop used by `edfxtp`. The six-model RedMulE recipe alone was insufficient.
Icarus tests compare all seven against the original tables. Original and derived
model hashes are recorded; no four-state or SDF equivalence is claimed.

The C++ reference writes retirement time one native tick after the corresponding
clock edge. The SV tracer writes at the edge. GLS measurement bounds therefore
start one tick after its retired start marker, while the retirement comparison
uses unshifted marker times. This preserves the same post-marker cycles and is
checked using relative clock-edge hashes after reference-clock conversion.

The power boundary is the complete mapped `ibex_top`, including its FF register
file, CSRs and synthesized RVFI observation logic. This differs from the RTL
activity proxy (`u_ibex_core`, excluding CSRs). Their toggle inventories are
not comparable as identical nets. RVFI contributes additional power; no
uninstrumented-core power claim is made. This is zero-delay functional GLS,
not timing closure at a two-picosecond clock or a signoff power result.

ICache is disabled and RegFileFF is selected. Internal inferred ROMs are
lowered to standard cells; the driver rejects residual unmapped/macro cells.
The original 262144x32 two-port synchronous system RAM is simulated with its
original byte-write/read-before-write model, outside the power boundary.
Existing single-port fakeram contracts are incompatible and are not substituted.
`memory_macros` is consequently empty. `power_libraries` maps each required
Liberty path to its hash; the manifest also records external memory exclusion,
simulation model hashes, configuration and source closure. Full-system RAM
power would require a separately validated dual-port macro and Liberty.

The shared power pipeline uses marker-bounded grids, separate RTL/GLS clocks, a qualified DUT scope,
verified Liberty lists and the explicit scope/instrumentation limitations.
