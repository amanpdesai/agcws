# Ibex calibration replay across runtime refresh

Replay all 64 original calibration programs, including the three useful-work
rejections. Validate the old calibration summary against the recorded bank
before freezing cases. No random regeneration or new normalization is allowed.
Use the same binary digest, Docker image, workload compiler and native evaluator
with the current verified source inventory; eighteen concurrent CPU workers.

Compare validity/stage, native allocation, complete execution/feedback records
and the entire activity profile except `extraction_s`, which is wall-clock
parser runtime rather than a measured hardware property. Waveform hash, source
hash, bin transitions/rates, timing markers, exclusions and unknown-state counts
must still match exactly. Do not weaken this comparison after seeing results.
Keep every mismatch. Promotion requires all 64 comparisons passing; successful
process completion alone is insufficient. No paid calls or target changes.

## Supplement: binary date metadata (declared before full comparison)

The in-flight replay's inspected calibration-08 mismatch is solely the raw FST
hash. Decoding both files shows `$date` differs (Sep 13 versus Sep 14); all
recorded rates, timing, execution and non-waveform profile fields match for that
case. This is not yet proof for the whole corpus. Keep the original strict
comparison and its failures unchanged.

After all 64 cases complete, verify original/new raw file hashes against their
records, decode each valid pair completely using `fst2vcd`, and hash every line
except the header `$date` group. Require every remaining declaration, timestamp
and signal update to match exactly. Record both dates and both semantic hashes;
invalid cases must reproduce the same rejection, allocation and execution data.
Use eight conversion workers. Any signal mismatch prevents normalization reuse.
The supplemental comparison does not erase the failed raw-file identity claim.
