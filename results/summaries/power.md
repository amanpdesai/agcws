# Completed mapped-gate power assessment

Completed finalist power, controls separate, aligned reference-mean normalization. Original failures and verified recoveries retained. No power-space solve gate or silicon-accuracy claim.

| Design | Random | GA | Phase-model | Flash-Lite | Gemini 3.8 |
| --- | ---: | ---: | ---: | ---: | ---: |
| aes | 0.20201 (80) | 0.18226 (80) | 0.08675 (80) | 0.18178 (80) | 0.00956 (80) |
| dma | 0.01240 (80) | 0.01064 (80) | 0.01031 (80) | 0.01568 (80) | 0.00076 (80) |
| ibex | 0.44162 (80) | 0.36848 (80) | 0.45908 (80) | 0.46237 (80) | 0.14481 (80) |
| mesh | 0.01994 (80) | 0.01559 (80) | 0.01636 (80) | 0.01381 (80) | 0.00670 (80) |
| redmule | 0.34437 (80) | 0.24364 (80) | 0.36067 (80) | 0.29578 (80) | 0.06143 (80) |

Entries are mean normalized RMS power error, with measured nonflat run count in parentheses. Normalization uses the duration-weighted mean of the fixed reference, not the activity span. Failed cases are absent, never replaced by zeros. `matched_strong` reports identical measured subsets for each comparator.

450/450 strong and 45/45 reference replays completed. 0 measurements remain excluded. Original failures and verified recoveries are retained separately. Ibex and recovered RedMulE measurements pass strict reconstruction or the per-case slew-clipping audit. Original control measurements remain separate.

Of 40 nonflat reference workloads, 40 meet the activity gate. Other reference comparisons describe workloads, not validation of the requested target. Reference modulation and the best constant approximation (the eight-bin mean) are retained for every task. 399/400 strong nonflat measurements beat their reference's constant approximation.

Reproduce with `.venv/bin/python paper/scripts/extract_power.py`. `--capture` is the one-time local collection capture and refuses archive overwrite. The five compressed archives preserve full measurement JSON, receipt hashes, selection cases, collection identities, and failed attempts. This verifies recorded measurements and comparison arithmetic, not an independent OpenSTA rerun.

Excluding Ibex leaves 320 measured pairs. Mean NRMSE is 1.961% for Gemini and 8.907% for the selected classical comparators. The comparison remains descriptive, not a power-space success rate.
