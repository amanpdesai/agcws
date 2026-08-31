# Runtime image

The image is the reproducible execution boundary for CHIA workers and EDA
tasks. The host only needs Docker and Git. Build from the repository root:

```bash
docker build -f docker/Dockerfile -t agcws:dev .
docker run --rm agcws:dev
```

The image installs distribution versions of Verilator, Yosys, and Icarus, and
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
make dev-install
make test PYTHON=.venv/bin/python
make lint PYTHON=.venv/bin/python
```

Run the basic image check with:

```bash
docker build -f docker/Dockerfile -t agcws:dev .
docker run --rm agcws:dev python -c \
  'import os; from pathlib import Path; print(Path(os.environ["AGCWS_LIBERTY"]).exists())'
```

The canonical toolchain smoke test is:

```bash
docker run --rm agcws:dev bash scripts/container_smoke.sh
```
```
