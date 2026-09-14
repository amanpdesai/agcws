# AES exact runtime replay

All 64 original calibration programs and all 18 admitted witnesses replayed
exactly under the updated runtime: validity, failure stage, eight activity rates,
and complete profiles including window and useful work. See `audit.json` and
the original/new fingerprint mapping in [the promoted bank](../qualified-bank-v2.json).
No targets, scale or tolerance changed. This does not claim policy equivalence.

`evidence/` packs the completed replay (734 hash-verified files). The sibling
JSON files retain frozen inputs and expectations. Restore evidence into a
`replay/` directory; the reference measurement manifest is embedded in its
manifest. Recreate `reference/manifest.json` from that embedded measurement to
run `analysis/runtime_replay.py audit` at the matching runtime. No cloud calls
are required. The original v1 bank remains unchanged.
