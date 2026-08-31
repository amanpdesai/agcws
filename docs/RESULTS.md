# Results status

This file records the strongest verified results currently present in the
repository. It is not the final paper result: the declared 10-seed,
multi-design factorial study has not yet been completed.

## Verified infrastructure

- `make verify`: 161 tests passed, one skipped; Ruff clean.
- `make research-smoke`: passed.
- `make container-smoke`: passed, including FuseSoC/Ibex source preparation
  and deterministic workload compilation.
- Both checked-in Liberty files contain `internal_power`, rise/fall power,
  leakage, capacitance, and clock-gating characterization.
- AES cross-PDK corpus: 10 shared workloads, Spearman rank agreement about
  `1.0`; see `out/aes-pdk-rank-20260831/corpus-validation.json`.

## Preliminary AES scalar study

The current strongest aggregate is generated from
`out/aes-baseline-matrix-complete` and reproduced at
`out/final-analysis/aes-baseline-aggregate.json`. It contains five policies,
five scalar targets, and five seeds per policy/target cell. The convergence
figure is `out/final-analysis/aes-baseline-convergence.png`.

In this corpus, all policies solve the high target (`q=0.90`) at least once;
the recorded solve rates are random `1.0`, mutation `1.0`, evolutionary `1.0`,
hybrid `1.0`, and one-shot agent `0.8`. The lower targets have no recorded
solves in these runs. These are descriptive preliminary results, not a claim
that one method is superior: the corpus is AES-only, has five rather than ten
seeds, and does not include Vertex-backed agent trials.

## Known limitations

- Ibex core elaboration and RTL/source closure are reproducible; the bounded
  Liberty-mapping probe has not completed a mapped netlist, so Ibex
  gate-level power is unsupported.
- DMA finalist OpenSTA reports have sparse activity annotation (about 1.31%
  for Sky130 and 0.77% for Nangate45 in the recorded run); they are retained
  as diagnostic evidence.
- Vertex credentials, exact model availability, and billing configuration
  are external prerequisites. No cloud-agent performance claim is made until
  `make vertex-preflight` passes and a real run records model and cost
  provenance.

The final report must replace this preliminary section only after the full
factorial run, statistical tests, finalist validation, and provenance audit
are complete.
