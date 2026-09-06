"""Event-free native VCD cuts aligned to the frozen clock-sample partitions."""
import hashlib
import itertools
import json
import re

from analysis.vcd_window import window


def grid(path, clock, expected_edges, windows=8):
    if expected_edges < windows or windows < 1:
        raise ValueError('invalid edge/window count')
    span = window(path)
    clock_ids, values, edges, stamps = set(), {}, [], set()
    header, time, previous_time = True, None, None
    with path.open() as stream:
        for line in stream:
            line = line.strip()
            if header:
                match = re.fullmatch(r'\$var\s+\S+\s+(\d+)\s+(\S+)\s+(\S+)\s+\$end', line)
                if match and match[3] == clock:
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
                    edges.append(time)
                values[ident] = value
    if len(clock_ids) != 1 or len(edges) != expected_edges:
        raise ValueError('ambiguous clock or unexpected rising-edge count')
    periods = {b-a for a, b in itertools.pairwise(edges)}
    if len(periods) != 1 or min(periods) <= 1:
        raise ValueError('clock must have a uniform multi-tick period')
    indices = [k * expected_edges // windows for k in range(windows + 1)]
    cuts = [span['first_timestamp'], *[edges[i]-1 for i in indices[1:-1]], span['last_timestamp']]
    if any(cut in stamps for cut in cuts[1:-1]):
        raise ValueError('proposed boundary is not event-free')
    durations = [b-a for a, b in itertools.pairwise(cuts)]
    if min(durations) <= 0 or sum(durations) != span['last_timestamp']-span['first_timestamp']:
        raise ValueError('invalid window partition')
    return {'span': span, 'clock': clock, 'clock_edges': len(edges),
            'clock_period_ticks': periods.pop(), 'edge_indices': indices, 'bounds_ticks': cuts,
            'durations_ticks': durations, 'durations_s': [d*span['timescale_s'] for d in durations],
            'edge_timestamps_sha256': hashlib.sha256(json.dumps(edges).encode()).hexdigest(),
            'boundary_rule': 'Internal cuts one tick before indexed edge; no timestamp at any cut.'}
