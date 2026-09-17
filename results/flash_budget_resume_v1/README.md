# Flash-Lite accounting-only resume — 2026-09-17

User authorized fixing budget accounting and resuming Mesh/RedMulE. Neither
cap is raised: each remains **$120**. No spend reset, response replacement,
re-sampling, model change, target change, or manifest rewrite is permitted.
AES/DMA/Ibex are already complete and are not resumed.

## Defect and conservative adjustment

The original meter treats an absent reasoning-token count as unknown usage and
retains the entire pre-call reservation: 200,000 input plus 8192 output tokens.
This exhausted caps even when the actual prompt-token count was present.

For successful responses with unknown usage but a valid reported input count,
replace **only the hypothetical input allocation** with that reported count.
Keep the frozen full 8192-token output reservation, including unknown reasoning.
Do not infer reasoning=0 or call this a measured bill. Known-usage estimates are
unchanged. API errors, missing responses, or invalid/missing input counts retain
their original reservations. New calls still reserve the original full bound
before sending, and the existing atomic ceiling checks remain in force.

At the reconciliation snapshot:

| Design | Original conservative liability | Adjusted conservative liability |
|---|---:|---:|
| Mesh | $119.935836 | $55.204954 |
| RedMulE | $119.929428 | $37.745404 |

These are list-price liabilities, **not Google-confirmed charges**. Cloud Billing
API access was disabled and no accessible BigQuery billing dataset was returned.
The user's approximately $50 console figure remains unreconciled. This change
does not attempt to infer discounts, credits, billing delays or missing tokens.

## Preservation and implementation

`maintenance/resume_budget.py` is an explicitly versioned administrative wrapper
around the original engine. It verifies the original frozen inputs, preserves
the original runner lock and checkpoint replay, and replaces only the Meter
class with `ReconciledMeter`. No `src/agcws` runtime file changes. This extension
is disclosed; it is not claimed that absolutely no executed code changed.

The per-run `accounting-amendment-v1.json` pins the wrapper hash, original manifest
hash and unchanged cap. Per-response `accounting-v1.json` records the old/new
reservation and hashes the original request/response records. Reconciliation is
recomputed from immutable originals on restart, so it cannot double-release
reservations. Unknown-response markers still prohibit duplicate requests.
Original budget-stop failure files remain as historical evidence.

Tests cover exact repeated settlement, cached-response replay without another
API call, new-response settlement, retained unresolved/error reservations, and
enforced spending ceilings. A pre-resume checkpoint hash inventory is retained
alongside this report; existing checkpoints are checked after restart.

Verification: full suite 804 passed (three existing warnings), then all eleven
focused accounting tests passed including the added cap-enforcement test; lint
clean. The pre-resume inventory covers 28,637 Mesh and 18,829 RedMulE records.
Both have zero unresolved calls and pass original frozen-input verification.

Run only with explicit paid authorization:

```sh
.venv/bin/python -u -m maintenance.resume_budget \
  --directory out/flash-lite-matched-v1/mesh --execute --allow-paid
```

RedMulE uses the same command with its design directory. Both remain in the
original study roots; they are continuations, not replacement runs.
