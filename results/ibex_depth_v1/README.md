# Ibex depth v1 — frozen, awaiting execution

48 closed-loop development trajectories: four targets × seeds 610–612 ×
Pro-4096, Flash-4096, random and behavior-coverage. Each runs to 128 proposals;
16/64/128 results are prefixes, not independently resampled runs. Total: 6,144
slots, including two common initial programs per trajectory.

See [protocol](../../docs/IBEX_DEPTH_V1_PROTOCOL.md) and
[code quality audit](../../docs/CODE_QUALITY_AUDIT.md). The producer and manifest
are committed before calls. This directory initially contains frozen inputs;
it is not evidence that the panel is complete. Complete compact evidence will
be archived as deterministic gzip objects, with a hash index and independent
audit. Heavy simulator traces remain scratch, not Git objects.
