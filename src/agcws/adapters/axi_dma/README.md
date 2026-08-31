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
VCD for each direction, and writes a provenance-bearing manifest. The checked-
in smoke workload contains four legal 1024-byte descriptors, satisfying the
4096-byte useful-work floor while respecting AXI 4KB boundaries.

This is intentionally not yet a coupled memory-copy model: read and write
channels are validated independently with deterministic models. Functional
source-to-destination copying and full `axi_dma` top-level power evaluation
remain the next harness milestone.

Manifests mark this boundary explicitly with
`simulation_backend=independent_channel_rtl_plus_python_memory_model` and
`coupled_axi_dma_top=false`; these results must not be used as coupled-DMA
claims.
