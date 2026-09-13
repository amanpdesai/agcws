# RedMulE pulse-guided witness qualification v2

This is a new CPU-only qualification procedure, motivated by v1 failures and
the completed pacing diagnostic. Preserve v1 in full; do not append these
evaluations to its fixed 256-proposal arms or compare sample efficiency with them.

All nine requested vectors in both v1 splits remain unchanged. So do the
calibration scale, 65536-cycle observation window, eight bins, tolerance 0.10,
non-flat floor >0.12 and functional/useful-work gates. No models are called.

Use the three size-16 single queued job traces from pacing-probe-v1, one per
operand pattern, with data seed 7500. Estimate a pulse from requested release
2048 through recorded completion, subtract idle activity 2 and clamp negative
residuals to zero. This is an approximate superposition model, not an oracle:
controller overhead, changing addresses and multiple-job interactions may violate
it. No predicted fit qualifies as a witness.

For each request and operand pattern, propose one program per job count 1..8.
Use a 256-cycle release grid, reserve the recorded pulse duration between jobs,
four deterministic initializations and three coordinate-descent sweeps. Seeds
are 7600 for development and 7700 for confirmation. Keep the best predicted fit
per count/pattern; record counts that cannot be placed. Maximum 24 candidates
per request, 432 over both banks. Freeze these candidates before any new replay.
The language remains unchanged: each job is a one-job phase, with size fixed to
16. This specialized witness constructor is not a claimed general search policy.

Replay every proposed program through the unchanged shared evaluator with 18
workers. Retain every failure and measured result, even when a prior candidate
already solves the request. Select the valid lowest measured error, ties by
candidate ID, and apply the unchanged qualification gates. Never replace a target
by its achieved profile or admit using a surrogate prediction. Hidden calibration
traces and witness programs do not enter agent payloads.

Using v1's failed requests for readiness engineering is explicit, not a new
held-out policy comparison. Full-study policy seeds and execution remain gated.
