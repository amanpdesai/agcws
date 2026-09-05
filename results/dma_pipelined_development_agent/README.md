# DMA semantic v4 development — complete panel

All 15 cells and 750 proposal slots are complete and independently audited:
five targets × three development seeds, 50 proposal slots per run.
`comparison.json` combines these cells with the complete 60-cell baseline
panel under identical target, seed, budget, calibration and backend settings.

The primary endpoint favors random: mean AUC 2.0764 versus the agent's
2.5116 (about 21.0% worse). The agent solves 12/15 runs versus random's
9/15, but solve rate is secondary and does not reverse the primary finding.
Agent validity is 79.2%. The recorded cost estimate is $0.7667, incomplete
because two calls have unknown usage. No held-out inference is made here.

The q=0.10 seed-102 cell records 32 invalid patch paths, two schema-bound
violations, and four empty slots after a provider 504. Missing usage for
that request is explicitly flagged: recorded cost is a lower bound.
Failures remain included, and v4 is unchanged during this panel.

The catalog-interface candidate is evaluated separately. V4's AES advantage
does not generalize to a DMA AUC advantage in this development panel.
Both outcomes remain in the evidence; no cross-design superiority is claimed.
