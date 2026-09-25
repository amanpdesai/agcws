# Docker

Run these commands from the repository root. Building requires Docker Buildx,
initialized submodules and network access.

## Build and check

```bash
bash tools/setup.sh
bash docker/build.sh
bash docker/run.sh bash docker/smoke.sh
```

The smoke checks tool availability, libraries and a DMA RTL simulation. It makes
no model calls. Tool pins live in [tools.lock](../tools/tools.lock), consumed by
the [Dockerfile](Dockerfile). Existing images are not modified until rebuilt.

The wrapper exports pinned tool submodules into a temporary BuildKit source
context. Local edits are excluded. Initialize nested submodules before building.

For the benchmark layer, set `AGCWS_BUILD_VARIANT=benchmark` and
`AGCWS_BENCHMARK_BASE_IMAGE` to a verified registry image with `@sha256:` digest.
Use a separate `AGCWS_CONTAINER_IMAGE` tag to preserve the parent image.

## Run

```bash
bash docker/run.sh python3 -m agcws doctor
```

By default, the wrapper mounts your checkout read-only and runs as your user.
Outputs persist in `out/container-runs/<uid>`. Temporary files do not persist.
Host credentials and tool overrides are not loaded automatically.

To check the installed code without mounting the checkout:

```bash
AGCWS_CONTAINER_CHECKOUT=0 bash docker/run.sh bash docker/smoke.sh
```

| Setting | Default or purpose |
|---|---|
| `AGCWS_CONTAINER_IMAGE` | `agcws:dev` |
| `AGCWS_CONTAINER_OUTPUT` | Host output directory |
| `AGCWS_CONTAINER_CHECKOUT` | `1` for local source, `0` for image-only execution |
| `AGCWS_CONTAINER_TMPFS_SIZE` | `8g` temporary filesystem |
| `AGCWS_CONTAINER_DEPS` | Optional read-only dependency directory |

## Cleanup

```bash
bash docker/prune.sh          # Preview
bash docker/prune.sh --apply  # Remove eligible project-owned resources
```

Cleanup targets this user's labeled project resources and dedicated builder,
not global Docker storage. Bind-mounted results are not deleted. Preserve the
images and tools required by frozen studies before pruning.

See [tools](../docs/TOOLS.md) and [workflow](../docs/ARCHITECTURE.md).
