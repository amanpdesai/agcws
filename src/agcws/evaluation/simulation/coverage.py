"""Measured Verilator basic-block coverage with stable source identifiers."""
import hashlib
import re
from pathlib import Path


def read_line_coverage(path: Path, root: Path, hierarchy: str) -> dict[str, int]:
    counters = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r"C '(.*)' (\d+)", line)
        if not match:
            continue
        descriptor, count = match.groups()
        fields = dict(part.split('\x02', 1) for part in descriptor.split('\x01') if '\x02' in part)
        instance = fields.get('h', '')
        if fields.get('t') != 'line' or not (instance == hierarchy or instance.startswith(hierarchy + '.')):
            continue
        stable = descriptor.replace(str(root.resolve()) + '/', '')
        point = hashlib.sha256(stable.encode()).hexdigest()
        counters[point] = int(count)
    if not counters:
        raise ValueError('no instrumented DUT line coverage points')
    return counters
