# Response-contract revision 2 — completed, readiness passed

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

Frozen at `74fa4fa9` before requests. Twelve fixed historical contexts, two arms,
24 requests and 48 charged slots. All calls finished with STOP, with no API errors
or unknown usage.

| Arm | Static-schema valid / 24 | Complete response adherence / 12 | Input tokens | Output including thinking | Estimated USD |
|---|---:|---:|---:|---:|---:|
| Original JSON-only | 16 | 8 | 126061 | 30445 | 0.1139308 |
| Explicit contract + simplified native schema | 23 | 11 | 126865 | 32199 | 0.1185570 |

The revised arm passes the predeclared >=90% static-schema readiness threshold.
Its one rejected program contains nine body operations, exceeding the unchanged
local limit of eight. No repair or extra proposal was granted. Server-side schema
relaxation did not relax the accepted workload language.

This is a paired fixed-context development diagnostic, not closed-loop search,
hardware validity, temporal AUC or held-out superiority. The output instructions
and native schema are a package; this comparison does not isolate their effects.
The original arm differs from the earlier 14/24 result because these are new
stochastic model requests, not reused responses. Both studies remain archived.

See [revision protocol](../../archive/README.md), `manifest.json`,
all input payloads and raw calls. Audit from the repository root:

```bash
python -m analysis.ibex_contract_v4 --root results/ibex_temporal_v4_contract_v2
```

Next: freeze a grounded temporal development panel only after the additional
execution/prediction readiness checks. Fresh held-out targets/seeds remain unused.
