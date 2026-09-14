# DMA window-v3 serialized witness proposals

Freeze this procedure and its generated config before executing any candidate.
Use the freshly calibrated 9,216-cycle bank, with the unchanged v2 analytic
fixed-mean shape procedure, 0.10 error tolerance and 0.12 non-flat floor gate.
No target may be replaced by a measured candidate's achieved profile.

For each of the eighteen requests (development and confirmation, eight non-flat
plus a separate control each), generate the three target-guided allocation
proposals described in SCHEDULE_WITNESS_REFINEMENT.md, now using the declared
9,216-cycle horizon. Then explicitly serialize every work unit into its own
one-unit operation. This disables concurrency in the native lowering and changes
the actual workload: it is a measured proposal, never an invisible repair.
The twelve timing corners motivated serialization before this search: depth-one
work spans the horizon; grouped work finishes earlier.

All 54 proposals are measured and charged, including duplicates or invalids,
with 18 CPU workers. There is no adaptive retry or extra budget. Keep every
result; choose the valid minimum-error witness among the three per request,
breaking ties by case identifier. Both native useful-work and functional checks
remain mandatory. Reconstruct rates from the DUT-scoped activity array and check
the 9,216-cycle window before accepting any witness. If requests remain unmet,
report them rather than extending this frozen version.

This is feasibility qualification, not a competitive policy arm. Its programs
must not be supplied as hidden initialization or privileged context to the LLM.
The future Flash/random/GA study still needs its own matched, frozen settings.
