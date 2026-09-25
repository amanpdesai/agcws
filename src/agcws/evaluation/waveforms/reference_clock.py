"""Explicit reference-clock conversion, preserving native waveform artifacts."""

from agcws.core.provenance import file_sha256 as sha


def reference_clock_vcd(source, target, factor):
    """Scale timestamps exactly, not values or event order; no timing-closure claim."""
    if type(factor) is not int or factor < 1:
        raise ValueError('reference-clock scale must be a positive integer')
    scale, header, last, first = [], True, 0, None
    in_scale = False
    with source.open() as src, target.open('x') as dst:
        for line in src:
            stripped = line.strip()
            if header:
                if '$timescale' in line:
                    in_scale = True
                if in_scale:
                    scale.extend(stripped.replace('$timescale', '').replace('$end', '').split())
                    if '$end' in line:
                        in_scale = False
                if '$enddefinitions' in line:
                    if ''.join(scale) != '1ps':
                        raise ValueError('reference-clock conversion requires native 1ps VCD')
                    header = False
            elif stripped.startswith('#'):
                tick = int(stripped[1:])
                if tick < last:
                    raise ValueError('VCD time reversal')
                first = tick if first is None else first
                last = tick
                line = f'#{tick * factor}\n'
            dst.write(line)
    if header or first is None:
        raise ValueError('incomplete native VCD')
    return {'source': str(source), 'source_sha256': sha(source),
            'waveform': str(target), 'waveform_sha256': sha(target),
            'integer_timestamp_factor': factor, 'timescale': '1ps',
            'native_first_tick': first, 'native_last_tick': last,
            'reference_first_tick': first * factor, 'reference_last_tick': last * factor,
            'native_duration_s': (last - first) * 1e-12,
            'reference_duration_s': (last - first) * factor * 1e-12}
