# RedMulE pulse-guided witness qualification v3

Only the proposal release grid changes from [v2](REDMULE_PULSE_WITNESS_V2.md):
16 cycles instead of 256. The v2 measurement completed before this revision.
All target vectors, gates, observation windows, model inputs, seeds, patterns,
job-count sweep, restarts, coordinate sweeps and real-evaluation limits remain
unchanged. Retain v2's full 340 replays and failed fits as separate evidence.

Motivation is measured pulse width, not a desired policy ranking: the 5th–95th
percentile excess-activity mass spans 251 cycles for alternating operands and
248 for random operands in the single-job diagnostic, after subtracting idle 2.
The coarse grid is approximately as wide as the switching pulse. It can skip
bin-boundary alignments that divide one pulse between neighboring bins. V3 tests
this numerical discretization issue; it does not relax target difficulty or claim
that a finer grid must solve every request.

Prepare using `scripts/qualify_redmule_pulses.py prepare --release-stride 16` in
a new directory, then execute that frozen manifest. Maximum remains 24 real
proposals per request. No extra attempts, target substitutions or model calls.
Record unplaced job counts, invalid replays and misses. Only real measurements
can qualify. This is readiness engineering on observed requests, not held-out
policy evidence. Historical v2 reproduction uses its frozen source commit.
