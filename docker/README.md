# Runtime image

The image is the reproducible execution boundary for CHIA workers and EDA
tasks. The host only needs Docker and Git. Build from the repository root:

```bash
docker build -f docker/Dockerfile -t agcws:dev .
docker run --rm agcws:dev
```

The initial image installs distribution versions of Verilator, Yosys, and
Icarus. OpenSTA and the selected Liberty file will be added once Slice 2 fixes
the synthesis/power flow; record their versions and checksums in provenance.
