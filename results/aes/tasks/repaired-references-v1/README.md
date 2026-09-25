# Repaired reference evidence v1

The same layout is used for aes, dma, ibex, mesh, and redmule. Each task
`bank.json` contains eight selected programs, frozen target vectors and scales,
manifests, qualification gates, and source identities. Selection used activity
only, never power or evaluated model finalists. Historical absolute paths are
provenance labels, not required local inputs.

`evidence.json.gz` is a gzip-compressed JSON object mapping member names to
`{sha256, text}`. Hashes cover UTF-8 text bytes. It contains selected native
qualification requests/measurements/receipts, functional evidence, frozen tasks,
original fixed-reference records where reused, and construction/selection scripts.
These scripts document original construction; they are not a promise that a new
RTL simulation can run without the separately archived toolchains and sources.

Power evidence lives in `results/<design>/power/repaired-references-v1/`.
Each target has its byte-identical native `measurement.json`. `index.json`
maps `references[target]` to `{path, sha256}` using repository-relative paths;
`inputs` lists portable evidence dependencies and hashes. DMA measurements are
exact copies from the original compact archive and are marked reused.

Power `evidence.json.gz` maps targets to source receipts and named proof files.
Each file has text and its SHA256. Large Ibex reports retain summary extracts
only, explicitly marked, with original complete-report hashes; saved slew-proof
receipts are included. Full per-pin slew reconstruction cannot be independently
repeated from these extracts. No waveforms, binaries, or netlist dumps are copied.

Verify all 40 qualifications and exact power joins without accessing `out`:

    PYTHONPATH=src python -m agcws.reporting.reference_repair verify --root .

The maintained publisher's `publish` and `package` commands capture the original
ignored-out source evidence. They never run experiments. To reproduce selection
logic, the original bank builder and verifier are embedded under `recipes/`.
