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

The Slang Yosys frontend is intentionally optional. Local runs can provide it
with `AGCWS_SLANG_PLUGIN`; container builds use the compatibility frontend until
a compatible plugin is added to the image.

Run the basic image check with:

```bash
docker build -f docker/Dockerfile -t agcws:dev .
docker run --rm agcws:dev python -c \
  'import os; from pathlib import Path; print(Path(os.environ["AGCWS_LIBERTY"]).exists())'
```
