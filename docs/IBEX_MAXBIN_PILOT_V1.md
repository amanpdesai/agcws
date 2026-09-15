# All-bin acceptance pilot

2026-09-15, explicitly requested after inspection of the RMSE pilots. Preserve
their original solve labels and the interrupted precision run. This is a new
exploratory protocol, not a correction to predeclared historical results.

Success now requires max(abs(achieved[i]-target[i])/scale) <= 0.05 across all
eight bins, plus existing validity gates. No time warping or relaxed edge bins.
RMSE still ranks search candidates and supplies best-so-far AUC. Record the
maximum-bin error separately; solved/censored and stopping use that maximum.
The success witness may differ from the minimum-RMSE candidate. No assertion
about within-bin cycle accuracy follows from bin averages.

Same alternating vector, two seeds, four arms, 128 slots, batch two and bounded
concurrency. Model payload explicitly states the all-bin gate and retains signed
per-bin feedback. Start fresh, no spliced LLM responses. Changed source files
are restricted to metric/stop logic, configuration and goal-payload dispatch;
simulation, compiler, activity, schema, binary and image identities are checked
unchanged during preparation. New source fingerprint is recorded, not bypassed.

Stop the old precision runner as requested, leaving completed and partial
checkpoints intact. Reserve all previous known/unknown liability against the
original combined $10 authorization; new cap is its remainder rounded down to
cents. Exhaustion halts this pilot without automatic additional spending.
Session `agcws-ibex-maxbin-v1`; log `out/ibex-maxbin-pilot-v1/runner.log`.
