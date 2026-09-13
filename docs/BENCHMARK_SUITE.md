# Five-design benchmark readiness

Started 2026-09-13. This is selection and admission work, not a frozen comparative
study. Existing studies and their target banks remain unchanged. The active goal
is five functioning shared-harness designs, cheap-model smoke tests and audited
target qualification. A failed candidate must be recorded, not silently replaced
after observing agent performance.

## Accelerated execution milestone

The user requests readiness work in one day. This is a scheduling target, not
permission to skip gates. BaseJump mesh and RedMulE are selected additions and
are pinned submodules at the inspected revisions below. Their unmodified RTL
is read-only. Large independent CPU jobs run concurrently; provider concurrency
is separately bounded. Flash is the only authorized smoke model.

The bank objective is eight substantive families plus a separate near-flat
control per design: sustained activation, sustained deactivation, isolated
burst, temporary quiet interval, repeated bursts, progressive ramp, rise/fall,
and irregular multilevel activity. These are requested families, not yet
qualified targets. Keep development and confirmation instances separate.
Qualification failures are part of the deliverable, not replaceable successes.

For new studies, 128 remains the proposal ceiling. Explicit `stop_on_success`
stops at the end of the first batch containing a valid tolerance hit. Charge all
requested siblings; retain exact first-hit slot and carry terminal best error
forward through the ceiling for AUC. Historical full-budget studies remain
unchanged; omitted early-stop configuration preserves their execution behavior.

Current bring-up: unmodified upstream BaseJump 2x2 and 3x3 all-to-all tests pass
under the existing immutable container with Verilator assertions enabled. Raw
commands/source hashes/logs are in `out/mesh-reference-gate`; this is a reference
gate, not target qualification or a new measured benchmark yet. RedMulE dependency
preparation is in progress. AES/DMA maintained-backend ports remain outstanding.

## Selection before agent outcomes

Keep Ibex, OpenTitan AES and verilog-axi DMA. Investigate two additions using
open RTL, explicit licenses, independent functional checking, temporal control,
distinct state/traffic mechanisms and realistic open-tool integration as criteria.
Do not select for a predicted agent win or equate module size with difficulty.

| Candidate | Experimental axis to test | Integration evidence and risk | Disposition |
|---|---|---|---|
| BaseJump mesh network, initially 2x2 | Source/destination contention, routing, buffering, backpressure and injection timing | Router RTL and all-to-all checked-delivery test exist; supplied Makefile uses VCS/cadenv, so open-simulator port is unproven | Preferred network addition, pending gate |
| PULP RedMulE | Matrix dimensions/tiling, operation selection, precision, compute versus memory service | Golden-model generation and Verilator flow exist; Bender dependencies include FP/control/streaming and processor test infrastructure | Preferred compute addition, pending gate |
| BaseJump cache | Locality, conflict misses, dirty evictions and refill latency | Dedicated regression sources exist; open-tool execution and reference-memory scoreboard need inspection | Alternate experimental axis, not automatically a sixth design |
| PULP HWPE MAC engine | Vector length/stride, multiply versus dot product, streaming stalls | Six RTL modules plus wrapper, hwpe-stream/ctrl dependencies; explicitly an example engine, not a high-performance accelerator | Lower-complexity compute alternative if RedMulE fails engineering gate |
| Gemmini | Tiling/dataflow and scratchpad/compute overlap | Strong architectural scope, but Chipyard/Rocket/software stack increases integration surface | Not first bring-up choice |
| verilog-ethernet UDP/IP stack | Packet sizes, ARP state, queues and traffic pacing | Cocotb tests exist; upstream is deprecated in favor of Taxi | Alternate; maintenance status must be explicit |

These proposed axes are hypotheses about useful experiments, not measured
activity ranges or evidence that agents reason about the hardware.

## Primary-source inspection

Read on 2026-09-13; shallow clones inspected outside the repository. No new
candidate is yet a pinned project dependency or a demonstrated backend.

- [BaseJump STL](https://github.com/bespoke-silicon-group/basejump_stl), inspected
  commit `11d19a888daa24e8239fc81c9c397b4d7bd58568`: Solderpad 0.51 root license;
  `testing/bsg_noc/bsg_mesh_router/all_to_all/{README.md,Makefile,sv.include}`.
  Test checks delivery from every tile to every tile. Its commercial-simulator
  invocation must not be presented as an existing Verilator reproduction.
- [RedMulE](https://github.com/pulp-platform/redmule), inspected commit
  `7fa9fbe8a29e8572810ae12b92c19749045ac860`: README declares Solderpad 0.51
  hardware and Apache-2.0 software, subject to file headers. Read `Bender.yml`
  and `target/sim/verilator/verilator.mk`. The latter includes `--bbox-unsup`:
  do not inherit this flag and call blackboxed behavior a verified DUT. Floating
  point checking must match actual rounding/accumulation, not assume host NumPy
  is bit-exact. Measuring a processor-driven testbench must exclude controller
  activity from the accelerator scope and record the interface actually exposed.
- [HWPE MAC engine](https://github.com/pulp-platform/hwpe-mac-engine), inspected
  commit `856875e39e14d079d73f32f04a59a162e8ae3bec`: README, Bender manifest and
  Solderpad 0.51 license inspected. Supports elementwise product and dot product
  plus addend, iteration strides and output normalization. Do not describe it
  as a systolic matrix accelerator or as equivalent to RedMulE.
- [Gemmini](https://github.com/ucb-bar/gemmini) and
  [verilog-ethernet](https://github.com/alexforencich/verilog-ethernet): upstream
  descriptions reviewed; no local build or dependency audit completed.

## Admission gates for every design, including Ibex

1. Pin RTL, transitive dependencies, configuration, tool/runtime identities and
   license notices. No DUT modifications or silent unsupported-cell blackboxes.
2. Compile and execute in the shared container path. Functional scoreboards
   check every completed result/packet/transfer, not just one convenient sample.
   Detect missing, duplicated, corrupted and unfinished work.
3. Define actual useful work and a fixed observation interval independently of
   target shape. Separate reset, warm-up, measured work and drain. Report work
   completed inside the window and total work; do not hide expensive drain work.
4. Verify deterministic per-bin activity, clock counting, DUT-only scope and
   reconstruction to whole-window counts. Exclude testbench/memory-driver activity.
   Activity is not watts; gate-power validation is separately labeled and gated.
5. Give all policies the same complete workload language and legality interface.
   Document design-specific engineering and adapter-imposed sequencing. Do not
   claim an adapter-discovered legal sequence was discovered by the model.
6. Freeze independent requested-shape generation and CPU witness-search rules
   before qualification. Record every attempt, budget, seed and failure. Keep
   witnesses inaccessible to the policy and measure reference error explicitly.
7. Include a legal near-flat control and non-flat difficulty levels; record
   constant-vector floors, pairwise distances, saturation, achievable range and
   near-floor validity. Hardness is measured baseline effort, not just a high
   constant floor. Analytic shapes alone do not prove reachability.
8. Audit Ibex polling/body contributions and boundary sensitivity; preserve the
   old eight-bin task but label its limits. Shifted windows and finer-bin checks
   are diagnostics, not post-hoc changes to the original success criterion.
9. Run Flash smoke with measured feedback, at least two model proposal batches,
   charged invalid/duplicate/missing slots, raw responses, model identity and cost.
   Freeze a small spending ceiling before calls; no blind repair or model fallback.
10. Restore compact evidence and re-run accounting. Smoke success establishes
    plumbing, not superiority, target-bank independence or semantic understanding.

## Work order

Inventory/selection → common backend contract and AES/DMA port → candidate
open-tool functional gates → per-design measurement and target qualification →
Flash smokes → evidence/reproduction. Independent cells may run concurrently;
feedback stays sequential within a trajectory. Build concurrency and provider
concurrency are separately bounded. No new paid comparative panel is authorized
by the smoke-test goal.

Readiness is per-design and per-gate, never inferred from a directory existing.
The maintained runner currently admits only Ibex; the five-design goal is not
complete until all five pass. If a preferred candidate fails, retain its failure
evidence and explain any substitution before inspecting agent performance.
