"""Versioned, streaming known-bit activity with explicit observation contracts."""

import hashlib
import re
from dataclasses import dataclass

CONTRACT = "known-bit-activity-v2"
_KNOWN = re.compile(r"[01]+")


def read_bits(path, observation):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        def lines():
            for raw in stream:
                digest.update(raw)
                yield raw.decode("ascii")
        result = stream_bits(lines(), observation)
    return {**result, "vcd": path.name, "waveform_sha256": digest.hexdigest(),
            "total_transitions": sum(result["window_bit_transitions"])}


def binary_state(text, width):
    text = text.lower()
    if not text or len(text) > width:
        raise ValueError("malformed VCD binary value or width")
    if _KNOWN.fullmatch(text):
        return int(text, 2), (1 << width)-1
    if set(text) - set("01xz"):
        raise ValueError("malformed VCD binary value or width")
    text = text.rjust(width, text[0] if text[0] in "xz" else "0")
    known = int("".join("1" if c in "01" else "0" for c in text), 2)
    value = int("".join("1" if c == "1" else "0" for c in text), 2)
    return value, known


@dataclass(frozen=True)
class Observation:
    scope: str
    clock: str
    cycles: int
    windows: int = 8
    begin: int | None = None
    end: int | None = None
    exclusions: tuple[str, ...] = ()
    require_known_initial: bool = False
    period: int | None = None

    def __post_init__(self):
        if self.cycles < self.windows or self.windows < 1 or "." not in self.clock:
            raise ValueError("explicit clock and positive observation required")
        if (self.begin is None) != (self.end is None):
            raise ValueError("both time boundaries required")
        if self.begin is not None and self.begin >= self.end:
            raise ValueError("ordered half-open boundaries required")
        if self.begin is not None and (self.period is None or self.period <= 0
                                       or self.end-self.begin != self.cycles*self.period):
            raise ValueError("marker window requires exact cycle duration and period")


def stream_bits(lines, observation):
    spec = observation
    widths, selected, clocks, values, ever_known = {}, set(), set(), {}, {}
    stack, samples, edge_ticks = [], [0]*spec.cycles if spec.begin is not None else [], []
    header, timestamp, last_tick = True, 0, 0
    previous_edge, period, clock_value = None, None, None
    group_bits, group_edge, initial_checked = 0, False, False
    initialized_bits, timescale, scale_pending = 0, None, False

    def inside(t):
        return spec.begin is None or spec.begin <= t < spec.end

    def flush():
        if inside(timestamp):
            if group_edge:
                edge_ticks.append(timestamp)
                if spec.begin is None:
                    samples.append(0)
            if spec.begin is not None:
                samples[(timestamp-spec.begin)//spec.period] += group_bits
            elif samples:
                samples[-1] += group_bits

    for raw in lines:
        line = raw.strip()
        fields = line.split()
        if not fields:
            continue
        if header:
            if fields[0] == "$timescale":
                scale_pending = True
                if "$end" in fields:
                    timescale = "".join(fields[1:-1])
                    scale_pending = False
            elif scale_pending:
                if fields[0] == "$end":
                    scale_pending = False
                else:
                    timescale = (timescale or "") + "".join(fields)
            elif fields[0] == "$scope":
                stack.append(fields[2])
            elif fields[0] == "$upscope":
                stack.pop()
            elif fields[0] == "$var":
                width, identifier = int(fields[2]), fields[3]
                name = ".".join([*stack, fields[4]])
                if width < 1 or (identifier in widths and widths[identifier] != width):
                    raise ValueError("inconsistent identifier widths")
                widths[identifier] = width
                if name == spec.clock:
                    clocks.add(identifier)
                if (name.startswith(spec.scope + ".") and fields[1] != "parameter"
                        and not any(x in name for x in spec.exclusions)):
                    selected.add(identifier)
            elif fields[0] == "$enddefinitions":
                header = False
                selected -= clocks
                if len(clocks) != 1 or not selected or not timescale:
                    raise ValueError("missing explicit clock, scope or timescale")
            continue
        if line.startswith("#"):
            new_time = int(line[1:])
            if new_time < timestamp:
                raise ValueError("VCD time reversal")
            if new_time != timestamp:
                flush()
                group_bits, group_edge = 0, False
            timestamp, last_tick = new_time, new_time
            if spec.require_known_initial and not initial_checked and inside(timestamp):
                if any(values.get(i, (0, 0))[1] != (1 << widths[i])-1 for i in selected):
                    raise ValueError("unknown carried state at measurement start")
                initial_checked = True
            continue
        if line[0] in "01xXzZ":
            text, identifier = line[0], line[1:]
        elif line[0] in "bB":
            text, identifier = fields[0][1:], fields[1]
        else:
            continue
        if identifier not in selected and identifier not in clocks:
            continue
        value, known = binary_state(text, widths[identifier])
        if identifier in clocks:
            if widths[identifier] != 1 or known != 1:
                raise ValueError("unknown or non-scalar clock")
            if clock_value == 0 and value == 1:
                if group_edge:
                    raise ValueError("multiple rising edges at one tick")
                if previous_edge is not None:
                    delta = timestamp-previous_edge
                    if delta <= 0 or (period is not None and delta != period):
                        raise ValueError("nonuniform clock")
                    period = delta
                previous_edge, group_edge = timestamp, True
            clock_value = value
            continue
        old_value, old_known = values.get(identifier, (0, 0))
        seen = ever_known.get(identifier, 0)
        if inside(timestamp) and seen & ~known:
            raise ValueError(f"known bit became unknown: {identifier} at {timestamp}")
        if inside(timestamp):
            group_bits += ((old_value ^ value) & old_known & known).bit_count()
            initialized_bits += (known & ~seen).bit_count()
        values[identifier] = (value, known)
        ever_known[identifier] = seen | known
    flush()
    if (header or len(edge_ticks) != spec.cycles or len(samples) != spec.cycles or period is None
            or (spec.period is not None and period != spec.period)
            or (spec.end is not None and last_tick < spec.end)
            or (spec.require_known_initial and not initial_checked)):
        raise ValueError("incomplete or mismatched observation")
    buckets = [samples[i*spec.cycles//spec.windows:(i+1)*spec.cycles//spec.windows]
               for i in range(spec.windows)]
    totals = [sum(b) for b in buckets]
    return {"activity_contract": CONTRACT, "clock": spec.clock, "scope": spec.scope,
            "exclusions": ["clock", "parameters", *spec.exclusions], "timescale": timescale,
            "clock_edges": len(samples), "period_ticks": period,
            "begin_tick": spec.begin if spec.begin is not None else edge_ticks[0],
            "end_tick": spec.end if spec.end is not None else last_tick,
            "per_cycle_toggles": samples, "window_bit_transitions": totals,
            "window_rates": [total/len(b) for total, b in zip(totals, buckets, strict=True)],
            "bin_edges": [len(b) for b in buckets], "selected_identifiers": len(selected),
            "selected_bits": sum(widths[i] for i in selected),
            "initialized_bits_in_observation": initialized_bits,
            "remaining_unknown_bits": sum(widths[i]-values.get(i, (0, 0))[1].bit_count() for i in selected),
            "units": "known bit transitions per rising clock edge; not watts"}
