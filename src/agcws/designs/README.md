# Design interfaces

The temporal study uses `temporal_registry.backend(domain)`. Each backend
defines a workload schema, proposals, feedback and measured execution.

| Design | Temporal backend | Execution and assets |
| --- | --- | --- |
| AES | `aes/backend.py` | `aes/simulate.py`, `aes/assets/`, `aes/gls.py` |
| DMA | `dma/backend.py` | `dma/simulate.py`, `dma/assets/`, `dma/gls.py` |
| Ibex | `temporal_registry.IbexTemporal` | `ibex/programs/`, `ibex/assets/`, `ibex/gls.py` |
| Mesh | `mesh/backend.py` | `mesh/simulate.py`, `mesh/assets/`, `mesh/gls.py` |
| RedMulE | `redmule/backend.py` | `redmule/simulate.py`, `redmule/assets/`, `redmule/gls.py` |

`workloads/` and `schedule_backend.py` provide shared schedule operations.
Design-specific construction and mutation stay with their backends.

The `adapter.py` interfaces exposed through `GENERIC_ADAPTERS` serve generic
command-oriented validation. They do not define the frozen temporal benchmark.
`validation.py` implements their schema, protocol and execution checks.

Upstream hardware sources are pinned under [benchmarks](../../../benchmarks/).
`assets/` holds our simulator inputs and harnesses, not upstream repositories.
