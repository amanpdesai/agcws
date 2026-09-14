# RedMulE long-window per-bin witnesses

All eighteen unchanged requests qualified under the frozen
[per-bin constructor](../../../docs/REDMULE_BIN_WITNESS_V1.md): eight nonflat
profiles and one flat control in each split. Measured normalized errors range
from 0.0110014 to 0.0386532, below the unchanged 0.1 tolerance.

Exactly 486 proposals completed: 267 valid, 219 rejected. Every candidate,
duplicate and rejection is retained. The packed archive restored and verified
2,470 files. `qualification-audit-v2.json.gz` additionally checks valid cached
program identity, native functional work and integer window activity arithmetic.
Its earlier selection-only audit remains inside the archive.

`requested-bank.json.gz` retains the original target vectors and explicit exact
calibration replay lineage. No request was replaced, softened or dropped.
The original short-window failures and 9,216-slot longer-window baseline
failure remain separate archives.

This proves witnessed feasibility, not policy performance. The constructor
uses measured activity and target-specific scheduling; its witnesses must not
be exposed to comparison policies. Public bank admission and current-runtime
Flash feedback smokes remain separate readiness gates. No full study launched.
