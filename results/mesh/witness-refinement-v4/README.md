# Mesh witness refinement v4 — target gate passed

All eight non-flat requests and the separate control qualify in both splits.
The [admitted activity bank](../qualified-bank-v1.json) preserves the original
requested vectors and their constant-vector floors and pairwise distances.
It contains witness identifiers, not witness programs for model input.

The [frozen refinement procedure](../../../docs/WITNESS_REFINEMENT_V4.md) used
140 charged slots total, including 18 initial exact replays. Previously missed
development burst/quiet-interval took 5/17 slots; confirmation quiet-interval,
alternating and irregular took 13/77/15 slots. Previously qualified targets
stopped after their exact initial replay. This is additional witness-search cost,
not a replacement for or fair policy comparison against v1's budgets.

The independent saved-evidence audit reconstructed every paired edit, incumbent
selection, batch-boundary stop and eight-bin rate from activity samples. It
checked functional completion records and 131 unique profiles. Both the audit
and admitted bank were regenerated identically using only the restored archive.
This does not independently resimulate waveforms. Raw scratch remains unchanged.

```sh
.venv/bin/python analysis/audit_witness_refinement.py --directory RESTORED --output NEW_AUDIT.json
.venv/bin/python analysis/audit_witness_refinement.py --directory RESTORED --admit-bank --output NEW_BANK.json
```

Target qualification is not full-study readiness. The Flash provider-grammar fix
still needs shared-loop integration and successful non-flat smokes. These are
RTL activity targets, not gate-power claims.
