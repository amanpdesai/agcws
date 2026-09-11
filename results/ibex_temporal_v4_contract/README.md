# V4 response-contract gate — completed, failed API readiness

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

Frozen at `53fb271b` before calls. All 24 requests and 48 requested slots are
recorded. The original JSON-only arm produced 14/24 schema-valid candidates;
the native full-schema arm produced none because all 12 requests returned HTTP
400: the schema's serving constraint had too many states. No repair, fallback or
retry was applied. This is not evidence that constrained generation worsens search:
the constrained arm never generated a response.

The original arm reports 126,061 input and 30,969 output tokens including thinking,
estimated $0.1152408. Rejected requests have no usage metadata and remain explicitly
unknown; their recorded zero estimate is not a claim of verified zero billing.
Readiness is false. No hardware simulation or temporal AUC was evaluated here.

`manifest.json` fixes settings and payload hashes, `inputs/` contains both arms'
contexts, `calls/` retains raw outcomes, and `sources/` preserves the frozen code.
The next development version will simplify the server grammar while retaining
the full local workload validator. It requires a separate freeze and run.

```bash
python -m analysis.ibex_contract_v4 --root results/ibex_temporal_v4_contract
```
