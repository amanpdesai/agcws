# `verilog-axi` DMA adapter

This adapter currently provides the design-independent workload contract for
descriptor-driven DMA experiments. A workload is a JSON object containing at
most 128 `transfers`; each transfer has aligned integer `src`, `dst`, and
positive `length` fields. Optional `outstanding` values request a bounded
channel depth from 1 through 8.

`validate_schema` and `validate_protocol` are pure and fast. `elaborate`
returns the validated descriptor sequence, while `useful_work` is completed
bytes.

The current deterministic harness is runnable with
`scripts/run_axi_dma_workload.py`. It drives the pinned RTL read and write
channel modules, checks descriptor completion and payload sequences, emits a
VCD for each direction, and writes a provenance-bearing manifest. Each transfer
artifact records the waveform SHA-256, raw per-cycle/window activity, and the
canonical max-normalized window profile. The checked-
in smoke workload contains four legal 1024-byte descriptors, satisfying the
4096-byte useful-work floor while respecting AXI 4KB boundaries.

The workload-driven coupled harness is available through
`scripts/run_axi_dma_coupled.sh`. It instantiates the pinned `axi_dma` top
level with a real AXI RAM, streams each read descriptor into the corresponding
write descriptor, and asserts source-to-destination byte equality. It is a
functional/protocol harness. The resulting waveform can be passed to
`scripts/run_axi_dma_cross_pdk.sh` for Sky130 and Nangate45 synthesis/OpenSTA
power validation; comparative DMA search studies remain separate.

The legacy runner's manifests retain
`simulation_backend=independent_channel_rtl_plus_python_memory_model` and
`coupled_axi_dma_top=false`; those results must not be used as coupled-DMA
claims. Coupled-harness logs are separately labeled by the script.
