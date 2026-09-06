# Frozen structural temporal study

Scope: goal-conditioned **activity-profile synthesis**, not established power-profile synthesis.

The development rule selected the **best-eight** family. The frozen study contains 160 cells / 5120 proposed slots: AES and DMA, two achieved reference profiles, four policies, ten fresh seeds (400–409), 32 slots per run and batch size four. Targets are previously observed profiles; fresh seeds do not demonstrate unseen-target generalization.

AES completes exactly 64 blocks in 6774 clock edges; DMA completes 4096 bytes in 12000 edges. Every method uses the same bounded schedule grammar and hard validity gates. Invalid, missing and duplicate proposals consume slots. Initialization is shared.

## Primary endpoint

Mean proposal-counted best-so-far loss AUC, lower is better. Loss is the predeclared fixed-scale capped NRMSE, not candidate-peak normalization.

| Design | Policy | Mean AUC | Solved | Capped evaluations-to-target | Valid slots |
|---|---|---:|---:|---:|---:|
| AES | Random | 3.31250 | 15/20 | 17.00 | 640/640 |
| AES | Evolutionary | 3.76097 | 12/20 | 24.35 | 640/640 |
| AES | Agent | 3.70269 | 8/20 | 26.80 | 562/640 |
| AES | Hybrid | 3.67449 | 9/20 | 25.00 | 590/640 |
| DMA | Random | 2.49243 | 20/20 | 8.35 | 640/640 |
| DMA | Evolutionary | 2.65497 | 18/20 | 10.50 | 640/640 |
| DMA | Agent | 2.73714 | 14/20 | 13.30 | 573/640 |
| DMA | Hybrid | 2.77839 | 18/20 | 11.10 | 610/640 |

Unsolved runs remain right-censored at 32; the capped value is not an estimate of time to eventual success.

## Paired inference

Two target differences are averaged within each seed, leaving ten seed units. Intervals are pointwise 95% bootstrap intervals (10,000 replicates). Exact two-sided sign flips use joint Holm correction over eight comparisons. Nonsignificance is not equivalence or proof of parity.

| Design | Method vs baseline | AUC difference | 95% interval | Holm p | Significant direction |
|---|---|---:|---|---:|---|
| AES | Agent vs Random | 0.39019 | [0.21067, 0.57034] | 0.03125 | Baseline better |
| AES | Agent vs Evolutionary | -0.05828 | [-0.18973, 0.05690] | 1.00000 | None |
| AES | Hybrid vs Random | 0.36199 | [0.09295, 0.66776] | 0.27344 | None |
| AES | Hybrid vs Evolutionary | -0.08648 | [-0.30631, 0.16830] | 1.00000 | None |
| DMA | Agent vs Random | 0.24471 | [-0.01151, 0.49974] | 0.60938 | None |
| DMA | Agent vs Evolutionary | 0.08217 | [-0.35081, 0.51444] | 1.00000 | None |
| DMA | Hybrid vs Random | 0.28596 | [0.02462, 0.56770] | 0.60938 | None |
| DMA | Hybrid vs Evolutionary | 0.12343 | [-0.22849, 0.48665] | 1.00000 | None |

## Validity, cost and runtime

| Design | Policy | Schema | Protocol | Functional | Useful work | Estimated USD | Unknown usage batches |
|---|---|---:|---:|---:|---:|---:|---:|
| AES | Random | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| AES | Evolutionary | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| AES | Agent | 78 | 0 | 0 | 0 | 0.49383 | 0 |
| AES | Hybrid | 50 | 0 | 0 | 0 | 0.27429 | 0 |
| DMA | Random | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| DMA | Evolutionary | 0 | 0 | 0 | 0 | 0.00000 | 0 |
| DMA | Agent | 67 | 0 | 0 | 0 | 0.47130 | 1 |
| DMA | Hybrid | 30 | 0 | 0 | 0 | 0.26177 | 1 |

Recorded configured-rate model cost is $1.50118; 2 batches have unknown provider usage. Unknown usage makes accounting incomplete, not zero-cost. CPU policies have no LLM charges, not zero compute cost.

Recorded model usage totals 2431745 input tokens and 308664 output tokens; unknown-usage batches are excluded.

Summed trial/evaluation time is 7591.39 seconds; summed proposal-generation time is 2664.94 seconds. These ledger totals exclude outer run-process startup and are not a controlled speed benchmark: shared-host load and overlapping finalist validation affect elapsed time.

## Predeclared finalist validation

16/16 selected seed-400 cases have matched validation, using 16 unique gate replays. Lowest-loss valid trials are selected without gate scores; ties use earliest proposal. Missing valid finalists remain missing. Duplicate cases are not independent measurements.

Successful unique replay pipeline time totals 2904.14 seconds (excluding synthesis, search and failed attempts). The archive records each waveform’s own timescale/span, functional checks, annotation and power components.

| Design | Target | Policy | Proposal source | Dynamic power (mW) | Annotated pins |
|---|---|---|---|---:|---:|
| AES | random_300 | Random | cpu | 4.457210 | 90247/90247 |
| AES | random_300 | Evolutionary | cpu | 4.457268 | 90247/90247 |
| AES | random_300 | Agent | model | 4.457268 | 90247/90247 |
| AES | random_300 | Hybrid | model | 4.457263 | 90247/90247 |
| AES | random_301 | Random | cpu | 4.457217 | 90247/90247 |
| AES | random_301 | Evolutionary | cpu | 4.457217 | 90247/90247 |
| AES | random_301 | Agent | model | 4.457217 | 90247/90247 |
| AES | random_301 | Hybrid | model | 4.457217 | 90247/90247 |
| DMA | random_300 | Random | cpu | 20.495125 | 36292/36296 |
| DMA | random_300 | Evolutionary | cpu | 20.494902 | 36292/36296 |
| DMA | random_300 | Agent | model | 20.494951 | 36292/36296 |
| DMA | random_300 | Hybrid | model | 20.495092 | 36292/36296 |
| DMA | random_301 | Random | cpu | 20.495151 | 36292/36296 |
| DMA | random_301 | Evolutionary | cpu | 20.495093 | 36292/36296 |
| DMA | random_301 | Agent | model | 20.494972 | 36292/36296 |
| DMA | random_301 | Hybrid | model | 20.495034 | 36292/36296 |

Dynamic power is internal plus switching, averaged over the matched full window. It is not temporal target error. Similar full-window means can coexist with different activity schedules at fixed useful work and duration. Proposal source distinguishes model improvements from shared initialization or CPU steps.

## Claim limits

The population ablation is AlphaEvolve-inspired, not AlphaEvolve itself. The selected controller applies bounded structural edits; it does not evolve arbitrary generator programs. DMA here uses fixed-size copies with pacing/concurrency, not the full transfer-length and backpressure space. Results do not establish random-search optimality or identify hardware size as the cause of any method ordering.

GLS uses functional zero-delay cell models. Full-window mean dynamic power does not validate the eight-bin temporal power shape, and no pooled cross-design proxy correlation is claimed. These are not signoff power results.
