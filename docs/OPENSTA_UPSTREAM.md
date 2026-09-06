# Pinned upstream OpenSTA

The native validation tool is now upstream OpenSTA commit
`a9a3f30ca97dc13f9ef911cae1a82c42c67379e1`. `.env` selects its absolute
`bin/sta` path. The existing system `sta` was not overwritten. Docker's source
pin is updated too, but no successful rebuild of that image is claimed here.

## Rebuild

Use a new installation directory and an existing CUDD 3.0.0 build. The host
build used GCC 13.3, static CUDD and disabled optional Tcl readline. For example:

```bash
git clone --no-checkout https://github.com/The-OpenROAD-Project/OpenSTA.git out/tools/opensta-a9a3f30/source
git -C out/tools/opensta-a9a3f30/source checkout --detach a9a3f30ca97dc13f9ef911cae1a82c42c67379e1
cmake -S out/tools/opensta-a9a3f30/source -B out/tools/opensta-a9a3f30/build \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DUSE_TCL_READLINE=OFF \
  -DCMAKE_INSTALL_PREFIX="$PWD/out/tools/opensta-a9a3f30" \
  -DCUDD_DIR="${AGCWS_CUDD_ROOT:?Set the CUDD build directory}" \
  -DCUDD_LIB="$AGCWS_CUDD_ROOT/cudd/.libs/libcudd.a"
cmake --build out/tools/opensta-a9a3f30/build --parallel 8
cmake --install out/tools/opensta-a9a3f30/build
.venv/bin/python maintenance/verify_opensta_windows.py \
  --source out/tools/opensta-a9a3f30/source \
  --binary out/tools/opensta-a9a3f30/bin/sta \
  --out out/opensta-window-verification
```

Set `AGCWS_OPENSTA` in `.env` to the resulting absolute executable path.
Shell environment overrides still take precedence. The source/build is ignored
under `out/`; preserve it while this installation is active, or rebuild from
the pin. The recorded verification is in `results/opensta_upstream_a9a3f30/`.

## Window behavior

`read_vcd` now accepts `-begin_time` and `-end_time`. Values are integer VCD
ticks: convert using that waveform's own `$timescale`, not the Liberty time
unit or an assumed nanosecond unit. The upstream regression verifies activity
and duty cycle, including carried-in state and partial windows.

Transitions at both endpoints are included. Adjacent closed intervals can
therefore count a boundary transition twice. A future eight-bin evaluator must
declare and test its boundary ownership and duration convention; it must not
blindly concatenate inclusive windows or change durations to hide the overlap.
Use isolated evaluations or explicitly clear prior power activity between reads.

## Verification and claim boundary

The upstream window regression matches its expected output exactly. Full-window
re-evaluation of one frozen AES finalist and one DMA finalist gives exactly the
same printed power components and annotation counts as the older tool. This
checks installation compatibility on those cases, not all possible inputs.

No archived search, finalist selection or prior power report was overwritten.
Future windowed results belong to this explicitly versioned validation tier.
Replaying an old frozen run requires its recorded tool settings (including the
old `AGCWS_OPENSTA=sta`); do not weaken the freeze check to accept the new path.
The 16-finalist eight-bin power study has not run, and activity target vectors
must not be interpreted directly as watts.
