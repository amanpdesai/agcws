"""Event-free native VCD cuts aligned to the frozen clock-sample partitions."""
import hashlib
import itertools
import json
import re

from agcws.evaluation.waveforms.span import window


def grid(path, clock, expected_edges, windows=8, *, begin=None, end=None):
    if expected_edges < windows or windows < 1:
        raise ValueError('invalid edge/window count')
    span = window(path)
    if (begin is None) != (end is None):
        raise ValueError('both marker-window boundaries are required')
    if begin is not None and not span['first_timestamp'] < begin < end <= span['last_timestamp']:
        raise ValueError('marker window must lie inside the waveform after initialization')
    clock_ids, values, edges, stamps = set(), {}, [], set()
    scopes = []
    header, time, previous_time = True, None, None
    with path.open() as stream:
        for line in stream:
            line = line.strip()
            if header:
                fields = line.split()
                if fields[:1] == ['$scope']:
                    scopes.append(fields[2])
                elif fields[:1] == ['$upscope']:
                    scopes.pop()
                match = re.fullmatch(r'\$var\s+\S+\s+(\d+)\s+(\S+)\s+(\S+)\s+\$end', line)
                if match and ('.'.join([*scopes, match[3]]) if '.' in clock else match[3]) == clock:
                    if match[1] != '1':
                        raise ValueError('clock must be scalar')
                    clock_ids.add(match[2])
                if line == '$enddefinitions $end':
                    header = False
                continue
            if line.startswith('#'):
                time = int(line[1:])
                if previous_time is not None and time < previous_time:
                    raise ValueError('nonmonotone VCD timestamps')
                previous_time = time
                stamps.add(time)
            elif line and line[0] in '01xXzZ' and line[1:] in clock_ids:
                if time is None:
                    raise ValueError('clock value precedes first timestamp')
                ident, value = line[1:], line[0]
                if values.get(ident) == '0' and value == '1':
                    if begin is None or begin <= time < end:
                        edges.append(time)
                values[ident] = value
    if len(clock_ids) != 1 or len(edges) != expected_edges:
        raise ValueError('ambiguous clock or unexpected rising-edge count')
    periods = {b-a for a, b in itertools.pairwise(edges)}
    if len(periods) != 1 or min(periods) <= 1:
        raise ValueError('clock must have a uniform multi-tick period')
    indices = [k * expected_edges // windows for k in range(windows + 1)]
    period = next(iter(periods))
    if begin is None:
        cuts = [span['first_timestamp'], *[edges[i]-1 for i in indices[1:-1]], span['last_timestamp']]
        checked_cuts = cuts[1:-1]
    else:
        if end - begin != expected_edges * period:
            raise ValueError('marker duration differs from expected clock cycles')
        # OpenSTA includes boundary events. Move each half-open bound back one
        # empty tick so every observed transition belongs to exactly one bin.
        cuts = [begin + i * period - 1 for i in indices]
        checked_cuts = cuts
    if any(cut in stamps for cut in checked_cuts):
        raise ValueError('proposed boundary is not event-free')
    durations = [b-a for a, b in itertools.pairwise(cuts)]
    expected_duration = end-begin if begin is not None else span['last_timestamp']-span['first_timestamp']
    if min(durations) <= 0 or sum(durations) != expected_duration:
        raise ValueError('invalid window partition')
    return {'span': span, 'clock': clock, 'clock_edges': len(edges),
            'clock_period_ticks': period, 'edge_indices': indices, 'bounds_ticks': cuts,
            'durations_ticks': durations, 'durations_s': [d*span['timescale_s'] for d in durations],
            'edge_timestamps_sha256': hashlib.sha256(json.dumps(edges).encode()).hexdigest(),
            'relative_edges_sha256': hashlib.sha256(json.dumps([e-cuts[0] for e in edges]).encode()).hexdigest(),
            'boundary_rule': 'Internal cuts one tick before indexed edge; no timestamp at any cut.'}
