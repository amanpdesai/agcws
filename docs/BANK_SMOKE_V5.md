# AES/DMA feedback follow-up v5

Frozen before any new call, 2026-09-14. This is an engineering smoke, not
paper inference or a retry of v4. Keep all v4 outcomes and reservations.

Run AES and DMA only, all eighteen admitted requests per design, Flash-4096,
phase-random and phase-GA. Seed 8503; sixteen proposal slots, batch two, two
shared initialization slots, no early stopping. Eighteen cell workers and one
provider worker per design. Each design permits at most 126 model calls and
has a $12 liability ceiling. No replacement seeds, automatic candidate repair,
fallback models or uncharged calls. The seed is fixed now, not selected by
outcome. Budget and target gates are unchanged from v4.

Interventions are signed exact-budget arithmetic in visible AES/DMA history
and a documented ten-minute request deadline instead of two minutes. The
deadline is sent to the server and stored in model settings in every new
manifest. SDK attempts stay at one. This changes two engineering settings;
it is not a causal ablation attributing improvement solely to arithmetic.

Preserve the strict audit (zero API errors, known usage, correct model and
actual generated measured feedback on every target). Report the separately
user-approved operational audit alongside it: a recorded server 504 may be
accepted only with two charged API-failure slots, no score, unknown usage and
retained cost reservation. Every request must have a durable response; unknown
error classes or unresolved requests fail. Successful calls must retain exact
model and usage accounting. Feedback is mandatory regardless of API errors.
Durable recovery is separately tested; it does not imply a failed request was
retried. No new full-study run is authorized by this smoke.

The deadline-only source change must receive a checked compatibility bridge
from the five v5 banks before preparation; never silently edit a frozen
manifest. Target vectors, normalization, witnesses, measurement implementation,
and image/binary identities must match. Original v5 calibration and witness
replays remain the measurement evidence; any bridge is labeled as static
transport-only compatibility, not a new simulation.
