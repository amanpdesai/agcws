# Requested target banks v1 — not qualified

Generated from independent calibration by `scripts/prepare_target_bank.py`, under
`docs/TARGET_QUALIFICATION_V1.md`. Each design has eight analytic families and a
separate flat control in each split. `requested_bank.json` preserves vectors,
constant-vector floors, pairwise distances and calibration provenance. The two
other JSON files are ordinary CPU-only witness-search configs for the maintained
pipeline; creating them does not execute a search.

AES and DMA both fail the necessary non-flatness gate for activation and
quiet-interval requests in both splits. Those vectors remain in the bank and are
not qualified. Mesh passes this necessary diagnostic, but no request is qualified
without a measured valid witness. RedMulE also clears the necessary floor gate in
both splits; its feasibility is not yet demonstrated. Mesh CPU witness searches
are running through the ordinary pipeline. No full paid study is authorized by
these files.
