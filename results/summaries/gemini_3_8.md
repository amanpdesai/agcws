# Completed strong-model comparison

Gemini 3.8 Flash, MEDIUM reasoning, 65,536 output-token ceiling. All 450 designated continuation runs completed. No new model calls.

| Design | Nonflat solves / 80 | Mean RMS-error AUC | Control solves / 10 |
| --- | ---: | ---: | ---: |
| aes | 80 | 1.2316 | 10 |
| dma | 78 | 3.7192 | 10 |
| ibex | 80 | 4.8559 | 10 |
| mesh | 80 | 2.2394 | 10 |
| redmule | 69 | 5.3261 | 10 |

Hash-verified packed trials, matched tasks and initializations, cached activity, residuals, strict success, stopping and AUC. No independent simulation, provider-payload replay or reconciled billing claim.

Post-completion analysis: one Holm family of 15 strong-vs-classical contrasts; seed units on the fixed observed bank. Flash inference unchanged.

Reproduce with `.venv/bin/python paper/scripts/extract_strong.py`. The results index locates each design archive and its retained-cache companion.

Accounting includes recorded liabilities, not independently reconciled bills. Power results are in `power.json`.
