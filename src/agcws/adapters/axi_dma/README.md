# `verilog-axi` DMA adapter

This adapter currently provides the design-independent workload contract for
descriptor-driven DMA experiments. A workload is a JSON object containing at
most 128 `transfers`; each transfer has aligned integer `src`, `dst`, and
positive `length` fields. Optional `outstanding` values request a bounded
channel depth from 1 through 8.

`validate_schema` and `validate_protocol` are pure and fast. `elaborate`
returns the validated descriptor sequence for a future AXI harness, while
`useful_work` is completed bytes. No RTL simulator is claimed yet: functional
completion and power evaluation remain blocked on the pinned `verilog-axi`
RTL harness slice.
