# Mesh bit-target witness refinement v1

2026-09-14. CPU-only, post-hoc feasibility engineering, not a policy comparison.
Preserve the 14/18 bit-v2 bank and every unsuccessful attempt. Four misses have
valid best candidates from phase-GA at slots 234–249, with errors 0.1096–0.1284.
Validity is 502–513 of 513 attempts per missed request. This motivates local
refinement, not a claim of infeasibility or a change to tolerance.

Freeze the four failed target vectors, scale, measurement fingerprint and best
valid starting programs from the completed bank. No target, RTL, interface,
observation window, calibration or useful-work change. The other four designs
are unaffected because runtime source is unchanged.

For each failed request, propose exactly 512 local mutations, seed 7500 plus
its lexicographic target index. Start with its lowest-error valid program.
Uniformly choose one phase and one numeric field (start, duration, packets),
then add or subtract one of 1, 4, 16, 64. Clamp only to the schema field bounds
before submission; protocol/aggregate failures remain charged and unscored.
Keep a candidate as the new parent only on strictly lower measured error.
No early stopping, extra retries, structural changes, target-specific operators
or LLM calls. Four target searches run concurrently. This is a deliberately
strong warm-started witness finder, not a fair baseline against frozen agents.

Record all submitted programs, parent transitions, validity and actual bin
rates. Recompute loss and admission at tolerance 0.1; retain every remaining
failure. Publish as a separate supplement, never overwrite the v2 bank. Witnesses
are engineering-only privileged data and must not enter model search payloads.
