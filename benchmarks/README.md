# Hardware benchmarks

Pinned upstream sources live here. Our workload languages, harnesses and adapters
live in [src/agcws/designs](../src/agcws/designs/).

| Design | Upstream source | Adapter |
| --- | --- | --- |
| AES | `opentitan/` | [aes](../src/agcws/designs/aes/) |
| DMA | `verilog-axi/` | [dma](../src/agcws/designs/dma/) |
| Ibex | `ibex/` | [ibex](../src/agcws/designs/ibex/) |
| Mesh | `support/basejump_stl/` | [mesh](../src/agcws/designs/mesh/) |
| RedMulE | `redmule/` | [redmule](../src/agcws/designs/redmule/) |

`support/bsg_fakeram/` supplies memory models. `support/liberty/` contains the
characterization libraries used by the synthesis and power flows.

Initialize the pinned sources with `bash tools/setup.sh` from the repository root.
Git records each revision. Final tasks and measurements remain in
[results](../results/), summarized in [Results](../docs/RESULTS.md).
