# Architecture

## Boundaries

`src/agcws/nodes/` contains design-independent tool stages; `adapters/` owns
per-design DSLs and legality; `flows/` contains CHIA wiring. The maintained
study runner is `src/agcws/pipeline/`. `scripts/` contains individual hardware
stages, not policy matrices. `validation/` retains matched GLS and native
OpenSTA window measurement. `maintenance/` handles explicit retention.

## Pipeline

`validate → prepare → run → export` is the single command surface.
Preparation freezes explicit targets, policies, seeds, budget, source hashes,
simulator identity and container digest. Execution requires `--execute`;
model policies additionally require `--allow-paid`. See [usage](PIPELINE.md).

The maintained study backend is Ibex temporal synthesis: one weighted RV32IM
phase language, compiler/interpreter, fixed observation window and eight rate
bins. AES/DMA hardware adapters and GLS stages remain available; their frozen
comparative runners remain in the [archive](../archive/README.md), not silently
ported to the new backend.

Policies propose; only the engine measures and checkpoints. Random,
phase-random, phase-GA, GeST-derived controls, ridge screening, Flash and Pro
share this loop. Filtered proposals consume slots but remain unmeasured
(`valid=null`); invalid trials have no loss. Duplicates may hit the common
cache but still consume slots. Missing model candidates consume requested
slots. Infrastructure errors stop instead of receiving fake validity scores.
Saved provider requests are never silently resampled.

SCHEMA → PROTOCOL → FUNCTIONAL → USEFUL WORK is a hard gate. Floors, scales,
horizons and tolerances are frozen per study, not global calibration defaults.
Earlier scalar adapters and temporal programs must not be conflated.

## Evidence

RTL transitions per cycle are activity, not watts. GLS plus characterized
cells and OpenSTA is a separate validation tier. Synthesis is cached by inputs;
workloads change simulation activity, not the netlist. Windowed power uses
measured boundaries and a reconstruction audit.

Raw responses, finish reasons, token usage, unknown-cost reservations and
immutable trials are retained. Best-so-far AUC uses the proposal axis;
unsolved cases are right-censored at budget. Study-specific inference is
separate from the runner's descriptive summaries.

`RESULTS.md` is the only findings narrative; `results/` holds compact evidence;
`out/` is scratch. Original protocols, reports, code and tests remain
byte-verifiable in `archive/legacy-source.tar.gz`.
