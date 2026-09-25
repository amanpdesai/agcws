# Package map

```text
cli -> studies -> search -> baselines or model providers
          |                    |
          +---- designs <------+
                  |
              evaluation
                  |
          reporting + evidence
```

| Package | Owns |
| --- | --- |
| `cli` | Public commands and argument handling |
| `studies` | Calibration, search execution and collection scheduling |
| `search` | Policy dispatch, model transport and recovery for new studies |
| `baselines` | Classical proposal policies |
| `designs` | Workload languages, adapters, simulation harnesses and replay |
| `evaluation` | Activity measurement, synthesis, simulation and power |
| `reporting` | Trial metrics, statistical analysis and result summaries |
| `evidence` | Archive storage, verification and frozen-result replay |
| `core` | Configuration, subprocess execution, contracts and storage |
| `integrations/chia` | Generic CHIA execution nodes |

## Boundaries to preserve

- `designs/temporal_registry.py` selects the five-design study backends.
  `designs.GENERIC_ADAPTERS` contains the separate command-oriented interfaces.
- `evaluation/activity/known_bits.py` implements the benchmark bit counter.
  `generic.py` supplies value-change profiles for generic nodes, with different
  normalization. They are not interchangeable measurements.
- `reporting/metrics.py` validates and summarizes charged trial records.
  `reporting/statistics/curves.py` summarizes supplied error curves.

Paper-specific extraction and plotting live in `paper/scripts/`, not here.
