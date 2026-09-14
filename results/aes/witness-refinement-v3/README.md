# AES witness refinement v3 — target gate passed

All eight non-flat requests and the separate flat control qualify in both splits.
The [admitted activity bank](../qualified-bank-v1.json) preserves the v2 requested
vectors, floors and pairwise distances. It exposes witness identifiers, not
witness programs for use in the agent payload.

The [frozen procedure](../../../docs/SCHEDULE_WITNESS_REFINEMENT.md) used 30 charged
slots: 18 exact parent replays and three explicit allocation candidates for each
of the four previously unqualified requests. Every case then met tolerance, so
no paired refinement batches were required. Development quiet-interval error is
0.005736; confirmation activation error is 0.011001. Both flat-control errors are
0.0002944. The v2 misses remain preserved and counted in their original archives.

The compact-evidence audit checks native source identity, initial replay, candidate
construction, batch charging and stopping, cache identity, completion records and
eight-bin arithmetic. It checks 27 distinct measured profiles. Restoring only
this archive reproduced the audit and admitted bank identically. It does not
independently rerun waveform simulation.

```sh
.venv/bin/python maintenance/archive_study.py restore --source results/aes/witness-refinement-v3 --destination RESTORED
.venv/bin/python analysis/audit_schedule_refinement.py --directory RESTORED --output NEW_AUDIT.json
.venv/bin/python analysis/audit_schedule_refinement.py --directory RESTORED --admit-bank --output NEW_BANK.json
```

These are target-qualification results, not held-out policy results. A targeted
allocation constructor helped find witnesses; its success must not be attributed
to an agent. Full Flash/baseline loop smokes and the final study freeze remain
required. Activity qualification is not gate-power validation.
