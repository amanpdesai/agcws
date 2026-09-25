"""Read each waveform's own time span without borrowing another tier's clock."""
import re

UNITS = {'s': 1.0, 'ms': 1e-3, 'us': 1e-6, 'ns': 1e-9, 'ps': 1e-12, 'fs': 1e-15}


def window(path):
    scale = None
    declaration = b''
    first = None
    with path.open('rb') as stream:
        for line in stream:
            if b'$timescale' in line or declaration:
                declaration += line
                if b'$end' in declaration:
                    match = re.fullmatch(rb'\s*\$timescale\s+(\d+)\s*(s|ms|us|ns|ps|fs)\s+\$end\s*', declaration)
                    if not match or int(match[1]) not in (1, 10, 100):
                        raise ValueError('invalid VCD timescale')
                    scale = int(match[1]) * UNITS[match[2].decode()]
                    declaration = b''
            if re.fullmatch(rb'#\d+\s*', line):
                first = int(line[1:])
                break
        stream.seek(0, 2)
        size = stream.tell()
        count = min(size, 65536)
        while True:
            offset = size - count
            stream.seek(offset)
            tail = stream.read(count)
            if offset:
                tail = tail.partition(b'\n')[2]
            stamps = re.findall(rb'^#(\d+)\s*$', tail, re.MULTILINE)
            if stamps:
                last = int(stamps[-1])
                break
            if count == size:
                raise ValueError('no VCD timestamps')
            count = min(size, count * 2)
    if scale is None or first is None or last <= first:
        raise ValueError('missing or nonpositive waveform span')
    return {'timescale_s': scale, 'first_timestamp': first, 'last_timestamp': last,
            'start_s': first * scale, 'end_s': last * scale, 'duration_s': (last-first)*scale}
