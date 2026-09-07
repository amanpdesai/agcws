"""Add address labels only; CPU-equivalence gate must verify emitted text bytes."""

from experiments.ibex_temporal_v3.program import (
    assembly as original_assembly,
    canonical,
)


def assembly(program):
    program = canonical(program)
    lines = original_assembly(program).splitlines()
    cursor = 0
    for i, segment in enumerate(program["segments"]):
        setup = lines.index(f"  li s9, {segment['release']}", cursor)
        lines[setup:setup] = _label(f"segment_{i}_setup")
        poll = lines.index(f".Lrelease{i}:", setup)
        lines[poll:poll] = _label(f"segment_{i}_poll")
        body = lines.index(f"  bltu t0, s9, .Lrelease{i}", poll) + 1
        lines[body:body] = _label(f"segment_{i}_body")
        cursor = body + 2
    return "\n".join(lines) + "\n"


def _label(name):
    return [f".global agcws_{name}", f"agcws_{name}:"]


def phases(symbols, segments):
    boundaries = [(symbols["measure_start"], "measurement_setup")]
    for i in range(segments):
        boundaries.extend(
            (symbols[f"agcws_segment_{i}_{phase}"], f"segment_{i}_{phase}")
            for phase in ("setup", "poll", "body")
        )
    boundaries.extend((symbols[k], k) for k in ("body_complete", "measure_stop"))
    if any(a[0] >= b[0] for a, b in zip(boundaries, boundaries[1:])):
        raise ValueError("phase addresses must be strictly increasing")
    return [
        {"begin_pc": a, "end_pc": b, "phase": name}
        for (a, name), (b, _) in zip(boundaries, boundaries[1:])
    ]
