# Mesh exact runtime replay

All 64 original calibration programs and all 18 admitted witnesses replayed
exactly under the updated runtime: validity, failure stage, eight activity rates,
and complete profiles including window and useful work. See `audit.json` and
the original/new fingerprint mapping in [the promoted bank](../qualified-bank-v2.json).
No targets, scale or tolerance changed. This does not claim policy equivalence.

`evidence/` packs the completed replay (742 hash-verified files). The sibling
JSON files retain frozen inputs and expectations. Restore evidence into a
`replay/` directory; recreate `reference/manifest.json` from the measurement
embedded in its manifest, then run `analysis/runtime_replay.py audit` at the
matching runtime. No cloud calls are required. The original v1 bank is unchanged.
