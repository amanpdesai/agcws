# Image-only matched replay — 2026-09-07

Two existing seed-400/random/random_300 finalists were replayed using the image's
own source, Icarus and pinned upstream OpenSTA, with no host source or tool mounts.
Only checksummed input artifacts and writable outputs were bind-mounted.

- Image: `agcws:window-validation-v1`
- Image ID: `sha256:9e0cb9653e368644baf5c5bd6a936f80bb12adb813baa18403fd96c5ea4f7d5a`
- Image size: 2,467,621,990 bytes.
- Dockerfile SHA256: `2662c2961d25b2a779f49c1ee6e75d82f97bf3e6f5288ea0dc71c9222e616ae5`
- Replay source SHA256: `9ba6370c3e392ce6a64d86d56621302de0984b6c949eb7a2f7845cb95f30114e`
- Runtime UID/GID: 1001/1001; read-only image, dropped capabilities, automatic removal.

AES completed 64 checked blocks over 6,774 clock edges in 389.39 seconds;
DMA completed the matched 4,096-byte schedule over 12,000 edges in 28.08 seconds.
The runs overlapped; these times are observations, not performance benchmarks.
For each design, the full window plus eight bins yielded 36 comparisons of
internal, switching, dynamic and leakage power. All 72 parsed values equal the
original archived host values exactly (predeclared acceptance: relative 1e-5,
absolute 1e-12 W). Functional observations, grids and annotation also match.

The per-design folders retain raw reports/Tcl, functional evidence, package
versions, input hashes and comparison records. Independently reconcile them:

```bash
.venv/bin/python -m analysis.audit_container_archive
```

To repeat with retained staged inputs, use a new output name:

```bash
AGCWS_CONTAINER_CHECKOUT=0 AGCWS_CONTAINER_IMAGE=agcws:window-validation-v1 \
AGCWS_CONTAINER_OUTPUT="$PWD/out/container-window-replay-v1" \
bash docker/run.sh python3 -m validation.container_replay \
  --inputs out/inputs --design aes --out out/aes-repeat
```

Use `--design dma` and a different output directory for DMA. Inputs are staged
by `maintenance.stage_container_replay` from retained existing finalists.
Mapped netlists and original RTL measurements were inputs, not regenerated
inside the image. This is not a clean-checkout synthesis test, a new research
comparison, or a rerun of either frozen study. The dirty CHIA example submodules
were not changed; this replay does not exercise those examples or Ray scheduling.
