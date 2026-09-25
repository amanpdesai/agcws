# Classical baselines

| File | Responsibility |
| --- | --- |
| `phase.py` | Ibex phase-random and phase-GA proposals |
| `temporal_model.py` | Temporal surrogate-guided proposals |
| `surrogate.py` | Ridge prediction, features and candidate screening |
| `controls.py` | Classical arm selection and matched controls |
| `screening.py` | Surrogate-screened genetic policy |
| `gest.py` | Hash-checked upstream genetic operator bridge |

[Search dispatch](../search/dispatch.py) connects classical and LLM policies to
the common study engine. Design-specific construction and mutation stay with
[design adapters](../designs/). Moving these files does not change policy IDs or
the frozen study implementations.

Upstream [GeST and GeST-SAGA](../../../tools/baseline-references/) remain pinned
submodules. GeST supplies checked genetic operators. GeST-SAGA supplies upstream
components checked by the test suite, not the final phase-model implementation.
See [final results](../../../docs/RESULTS.md) for the evaluated policies.
