# Matched RedMulE GLS

`python -m agcws.designs.redmule.gls` exposes three stages:

* `prepare --source-list FILE --dependency-root DIR --out NEW_DIR --liberty FILE --plugin FILE`
* `synthesize --out PREPARED_DIR [--yosys EXECUTABLE]`
* `replay --prepared PREPARED_DIR --reference RTL_ATTEMPT --out NEW_DIR --cells FILE --primitives FILE [--frozen-receipt FILE]`

The reference directory must contain the original `program.json`, `provenance.json`,
`run.log`, `activity.vcd`, generated `inc/` headers, and `build/stim_{instr,data}.txt`.
Replay copies those exact instruction/data images. It requires identical reference
completion cycles, output-check counts, useful work, accepted bus-trigger edges,
and observation bounds. It emits a success receipt only after all checks pass.
An optional frozen replay receipt is hashed and forwarded, not independently
reinterpreted as authorization or proof of frozen runtime identity. The shared
frozen bridge remains responsible for verifying the original measurement runtime.

The synthesis top is `agcws_redmule_4x4`; `gls.ports()` is its explicit port contract.
It instantiates the original `redmule_mm_wrap` at Height=Width=4, DataW=128,
NumPipeRegs=1, MisalignedAccessSupport=1, EnableReordering=0, LatchBuffers=0.
HCI has DW=160, AW=32, BW=8, UW=1, IW=8, EW=EHW=1. Peripheral ID width is 4.
Other accelerator defaults remain those of the hashed dependency closure.
The CPU, reference-checking software, external memory model, and reset sequence
are retained; only the accelerator instance is replaced. Accelerator storage is
mapped to logic; no SRAM black-box contract is substituted. Clock-gating latches
are explicitly mapped to SKY130 HD `dlxtn_1` (negative-level enable). Accordingly
this recipe requires SKY130 HD Liberty/models containing that cell. All final
cells must be found in the supplied Liberty; unknown cells reject synthesis.

For shared windows/grid wiring:

* Clock: `redmule_tb_wrap.clk`; scope: `redmule_tb_wrap.i_redmule_tb.i_redmule_wrap`.
* `expected_period_s=1e-9`, VCD timescale 1 ps, rising edges `500 + 1000*i` ps.
* N is exactly 65,536 or 262,144 and includes reset and CPU boot.
* First edge: 500 ps. Last edge: `N*1000-500` ps. Finish: `N*1000-499` ps.
* Use full-waveform edge-based windows (`bounds=None`) for the preserved metric.
  Do not invent a final `N*1000` ps timestamp: the harness ends half a cycle earlier.
  Explicit fixed-duration windows requiring a trace through that endpoint need
  a separately authorized measurement change, not a source-path alias.

Successful output is `gls_receipt.json`, `functional.json`, `activity.vcd`, and
logs. The receipt includes exact observed bounds, library/model hashes, mapped
netlist and synthesis-manifest hashes, original software-image hashes, reference
provenance hash, simulator version/binary hash, and waveform hash. This is
zero-delay functional GLS, not SDF timing validation or a power result.
Preparation and unit tests alone do not establish mapped functional correctness.
The common dispatcher uses `agcws.designs.redmule.container`, which pins the
installed image ID and validates container-scoped source paths inside that image.

Shared dispatcher entrypoints are in `agcws.designs.redmule.matched`:
`synthesize_trial(prepared_dir) -> dict` emits standard `manifest.json`;
`synthesis_manifest(prepared_dir)` publishes it for an already successful build;
`replay_trial(rtl, synthesis, out) -> dict` performs replay and returns waveform,
rtl_waveform, clock, rtl_clock, STA slash scope, clock_port (`clk_i`), clock_edges,
bounds (`None`), expected_period_s (`1e-9`), and receipt path. Model/tool paths use
the existing `AGCWS_SKY130_CELL_MODELS`, `AGCWS_SKY130_PRIMITIVES`,
`AGCWS_VERILATOR`, and `AGCWS_FST2VCD` environment variables. Compile parallelism
is `AGCWS_REDMULE_GLS_JOBS` (default 4). Optional
keyword `frozen_receipt=Path(...)` forwards the upstream frozen-runtime receipt;
no process-global environment variable is used for this per-trial identity.
Standard manifest sources are relative to the explicit `source_root`. The caller
must validate that declared root in its container or explicitly map it to the host
checkout and verify every hash. Detailed preparation paths remain container paths.

Integration evidence (2026-09-21): `prepared-v6` contains 99,645 validated SKY130
cells. `replay-v6/gls_receipt.json` records a successful mapped replay of the
original four 16x16 jobs: 1,024 checked outputs, 16,384 MACs, zero errors,
completion cycles [7312,13752,20316,27324], and trigger edges
[4579,11019,17583,24591]. All match the original RTL attempt exactly. The
65,536-edge window ends at 65,535,501 ps. Artifacts live under
`out/redmule-gls-validation/`; `replay-v6/matched_replay.json` is the dispatcher
return. This run validates this workload/short window, not every legal workload
or the long window. No frozen-runtime bridge receipt was supplied for this probe;
finalist collection must supply its separately verified receipt.

The successful dispatcher run used `/usr/bin/verilator` 5.032 (recorded in the
receipt); Mesh's successful host run used 5.048. Both use byte-identical official
cell/primitive files. Six UDPs required by RedMulE are translated in `compat.py`
to known-input, two-state functional equivalents, with the source revision pinned
and original licenses retained. Icarus regression compares those implementations
against the original UDPs for clock/reset/set/hold transitions and every known
mux input. This does not claim four-state or SDF equivalence. The derived model
hash is in receipt inputs alongside the original model hashes.

The only CPU diagnostic waiver is BLKANDNBLK in `cv32e40p_cs_registers.sv`:
non-implemented counter indices are tied off while distinct implemented indices
are clocked; event upper/lower slices are also disjoint. No CPU assignments are
changed. Full mapped replay verifies the resulting CPU-driven transactions and
reference output checks against RTL, including exact completion cycles. No
`--bbox-unsup`, black-box cells, or disabled reference checks are used.

The frozen `confirmation-activation` reference subsequently passed the long
262,144-edge replay (`frozen-long-rtl-v4`, `frozen-long-gls-v1`). All eight archived
RTL rates reproduced exactly. Its 1 ns OpenSTA replay annotates all 376,016 pins,
but fails switching-power reconstruction by about 2%. Per-cell diagnosis
(`frozen-long-power-debug-v1`) localizes essentially the entire difference to
clock inverter `_180612_`. OpenSTA's `PropActivityVisitor::setActivityCheck`
clips density to reciprocal minimum slew. Full-window and active-bin power for
this cell saturate at the same value, breaking the linear reconstruction.
The failed 1 ns result is retained, not admitted as validated power. A separately
labeled 10 ns timestamp-scaled diagnostic passed. The user approved this common
reference clock on 2026-09-21. The host dispatcher now produces separate 10 ns
power VCDs for both tiers, retaining native artifacts and conversion hashes without
changing native waveforms, workloads, or frozen activity scores.

Frozen replay needs a real `out` directory in its source checkout, not the
paused-run runtime's host-output symlink. `power-f4f4c1b3cf` is a separate copy of
the same verified source inventory, without that symlink or a copied `.env`.
The bridge resolves and verifies the dependency root before changing directories.
