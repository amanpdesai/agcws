# v4 smoke failure diagnosis — 2026-09-14

Operational-readiness approval does not excuse unexplained failures. This
read-only diagnosis covers all 630 recorded Flash calls, not a selected retry.
The original strict audits and all failed slots remain unchanged. No new model
calls were made for this diagnosis.

## API deadlines: a local configuration problem

`src/agcws/pipeline/model.py` sets `HttpOptions(timeout=120000)` with one SDK
attempt. The installed SDK converts milliseconds to seconds and sends
`X-Server-Timeout: 120`, in addition to setting the HTTP transport timeout.
The offline test `tests/test_vertex_deadline_diagnostic.py` exercises our actual
`generate()` function through the installed SDK and a mocked HTTP transport;
it confirms both settings without credentials or a network request.

| Design / target | Failed slots | Elapsed seconds | Next scheduled call seconds |
|---|---|---:|---:|
| DMA / confirmation-burst | 3–4 | 119.6502 | 21.0307 |
| Mesh / confirmation-activation | 9–10 | 119.6286 | 26.2125 |
| Mesh / development-flat_control | 11–12 | 118.6132 | 33.0204 |
| RedMulE / development-ramp | 7–8 | 119.4187 | 17.2316 |

All four return `ServerError`, HTTP 504, `DEADLINE_EXCEEDED`, with message
`Deadline expired before operation could complete.` None is a recorded 429 or
local transport exception. They occurred at different times, not one shared
shutdown. Every next scheduled call returned `STOP`; these were subsequent
budgeted proposals, not retries or replacements of the failed slots.

The timing, SDK behavior and Google's documented explanation strongly support
our client-specified deadline as the cutoff. Calling these merely server-side
errors was incomplete. We cannot recover the provider's internal reason for
the slow tail, or prove those requests would succeed with a longer deadline.
Queueing, generation latency and other backend delays remain unobserved.
There is no evidence here establishing quota exhaustion or a provider outage.

Sources: [Google API error guidance](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/api-errors)
and [SDK request construction](https://github.com/googleapis/python-genai/blob/main/google/genai/_api_client.py).
The local mocked-request test, rather than a moving upstream branch, establishes
the behavior of the installed SDK used here.

All eight failed slots are charged, receive no score, and retain $0.40384 total
unknown-call reservation. Durable-meter tests confirm saved failures are reused
on resume without resampling, and later scheduled calls can succeed. Operational
approval does not turn this into a zero-error run or erase the reservation.

## Exact-budget compliance: independent of API failures

Each AES/DMA candidate must total 64 work units and 6,000 idle cycles, including
repeat multiplicities. Recorded rejection messages already exposed actual and
required totals; the problem was not complete absence of corrective feedback.

AES `development-quiet_interval` has twelve protocol-rejected generated slots
(3–14). Slot 13 has 64 work / 5,000 idle; slot 14 has 48 work / 4,600 idle.
Slots 15–16 finally pass, but there is no later call in the frozen 16-slot
protocol to consume their measured feedback. Thus it fails the feedback gate,
not because no valid candidate was ever generated.

DMA `confirmation-burst` loses slots 3–4 to the deadline, then all remaining
twelve generated slots fail exact totals. Slot 15 has 64 work / 5,100 idle and
slot 16 has 64 work / 4,750 idle. Fixing the API deadline alone therefore cannot
justify declaring this target feedback-ready.

Across all generated slots (excluding shared initialization), AES has 124 valid,
122 protocol and 6 schema outcomes; DMA has 119 valid, 129 protocol, 2 schema
and 2 API outcomes. These are substantial compliance limitations, not isolated
cloud incidents. The implemented v5 signed arithmetic feedback is a testable
intervention, not a demonstrated fix: it still needs its bounded prospective
feedback check. Never auto-repair candidates or weaken the exact totals.

## Output truncation: a separate recorded failure

AES `development-deactivation`, batch 003, returned `MAX_TOKENS` after 59.97s:
4,664 input, 12,274 candidate and 4,095 thinking tokens. Both slots were schema
rejected. This is distinct from the 504s and from the quiet-interval feedback
failure. Other non-API responses returned `STOP`; `STOP` alone does not certify
schema validity. Do not relabel truncation as a generic inability to reason.

## Next gate

Before another paid smoke, explicitly version the transport-deadline policy,
test its effective server header and capture it in provenance. Remove the
unjustified two-minute cutoff; do not add hidden SDK retries or rerun v4 for
a cleaner result. A server-default or longer documented deadline is not a
guarantee that the provider will never fail.

Then freeze the bounded AES/DMA v5 arithmetic-feedback procedure. Operational
readiness still requires actual measured generated feedback on every target,
with every failure charged and unknown liability retained. The full study
remains unlaunched and is not ready merely because operational errors may now
be accounted for. Runtime edits require an explicit source-compatibility bridge;
they must not silently invalidate or relabel the current v5 banks.
