# Runtime image

## Managed containers and cleanup

Use `bash docker/build.sh` for future builds and `bash docker/run.sh <command>`
for container tasks. The build uses a dedicated `agcws-<uid>` builder rather
than this shared host's default cache. The run wrapper uses `--rm`, an init
process, the caller's UID/GID, dropped capabilities, a read-only root and
checkout, an 8 GiB temporary filesystem, and bounded container logs.
This host's Snap Docker rejects its init executable with `no-new-privileges`;
the tested wrapper does not set that option or use privileged mode.

The dedicated builder enables automatic cache garbage collection with a
30 GB target and a 10 GB retained cache floor (`docker/buildkitd.toml`).
These are garbage-collection thresholds, not a hard disk quota during a build.

Only `/workspace/out` persists, at `out/container-runs/<uid>` on the host by
default. Override `AGCWS_CONTAINER_OUTPUT`, `AGCWS_CONTAINER_IMAGE` or
`AGCWS_CONTAINER_TMPFS_SIZE` explicitly as needed. The wrapper does not load
host tool-path overrides or cloud credentials automatically. Existing frozen
held-out experiments are host executions; do not silently switch them to a
different container toolchain mid-study.

Set `AGCWS_CONTAINER_CHECKOUT=0` to execute the code baked into the image,
without mounting host source. In that mode only `/opt/agcws/out` is writable
and persistent. This is the appropriate mode for portability checks; default
checkout mode remains useful for development. The matched replay entry point
is `python3 -m validation.container_replay`, with checksummed inputs staged by
`python -m maintenance.stage_container_replay --out <new-input-directory>`.
It checks existing netlists, functional behavior and eight-window power, not
fresh synthesis or a rerun of the frozen policy studies.

```bash
bash docker/run.sh python3 -c 'import agcws; print(agcws.__version__)'
bash docker/prune.sh          # preview owned stopped containers/dangling images
bash docker/prune.sh --apply  # project + caller labels; dedicated builder only
```

Pruning removes owned stopped containers/dangling images older than 24 hours,
and unused dedicated-builder cache older than seven days while reserving
10 GB. It never runs global system/volume/default-builder pruning. Keep the
tagged runtime image and useful build cache for fast starts. Docker `--rm`
does not delete bind-mounted experiment outputs; see `maintenance/README.md`.
The rebuilt `agcws:window-validation-v1` image passed image-only AES/DMA
matched GLS and window-power replays on 2026-09-07. All 72 power components
matched archived host values exactly. See the [evidence and scope](../results/container_window_replay_v1/README.md).
The older `agcws:dev` tag was not silently replaced; select the verified tag
explicitly or rebuild the default tag with `docker/build.sh`.

See Docker's [pruning guidance](https://docs.docker.com/engine/manage-resources/pruning/)
and [builder-specific cache pruning](https://docs.docker.com/reference/cli/docker/buildx/prune/).

The image is the reproducible execution boundary for CHIA workers and EDA
tasks. The host only needs Docker and Git. Build from the repository root:

```bash
bash docker/build.sh
docker run --rm agcws:dev
```

The image installs distribution versions of Verilator, Yosys, and Icarus, and
pins FuseSoC to 2.4.6,
builds OpenSTA from the pinned `OPENSTA_REF` in the Dockerfile. The checked-in
Sky130 and Nangate45 Liberty files and the OpenTitan RTL submodule are copied
into the image. Build-time network access is required for the OpenSTA source;
the commit is pinned so the resulting tool is reproducible.

The image also builds the pinned `sv-elab` Yosys/Slang frontend and configures
it for full OpenTitan AES synthesis. Host runs may override
`AGCWS_SLANG_PLUGIN` with an explicitly verified compatible plugin; the
compatibility frontend is retained only for reduced/simple sources.
The build restores the Slang checkout's GitHub remote prefix and uses Slang's
vendored Boost compatibility headers. The regex dependency is explicitly
cloned and pinned to the resolved commit behind its annotated release tag,
then supplied to CMake as a local FetchContent source.
Toml++ is also supplied by the base distribution; optional mimalloc is disabled
to avoid another network-fetched dependency.
The image also supplies the small `yosys-config` compatibility wrapper expected
by `sv-elab`, since Debian packages the Yosys binary without that helper.

For a host development environment, use the repository-local virtualenv:

```bash
make install
make test VENV_PYTHON=.venv/bin/python
make lint VENV_PYTHON=.venv/bin/python
```

Run the basic image check with:

```bash
bash docker/build.sh
docker run --rm agcws:dev python3 -c \
  'import os; from pathlib import Path; print(Path(os.environ["AGCWS_LIBERTY"]).exists())'
```

The canonical toolchain smoke test is:

```bash
docker run --rm --user "$(id -u):$(id -g)" agcws:dev bash scripts/container_smoke.sh
```

The smoke is designed for arbitrary non-root UIDs: the image uses `/tmp` for
FuseSoC's cache and provides a writable `/opt/agcws/out` work root. For a
mounted checkout, set an explicit writable artifact root rather than reusing
old root-owned output directories:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD:/workspace" -w /workspace \
  -e AGCWS_ARTIFACT_ROOT=/tmp/agcws-artifacts \
  agcws:dev make run-ibex
```

Local `make test` and `make lint` use the host checkout because the image does
not package the repository's tests or Makefile. Inside the
image, use `scripts/container_smoke.sh` as the supported end-to-end toolchain
check; use the mounted-checkout command above for targeted checks.

The image also includes the optional analysis dependencies and the checked-in
`analysis/` tools, so activity figures can be generated inside the same
reproducible environment.
