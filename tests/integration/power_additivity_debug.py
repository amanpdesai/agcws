"""Localize a failed window reconstruction without relaxing its acceptance gate."""

import argparse
import concurrent.futures
import json
import re
import subprocess
from pathlib import Path

from agcws.core import config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--power', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    record = json.loads((args.power / 'power.json').read_text())

    def measure(name):
        text = (args.power / f'{name}.tcl').read_text()
        needle = '    incr leaf_count'
        assert text.count(needle) == 1
        text = text.replace(needle, '    puts "AUDIT_LEAF [get_full_name $inst] [format %.17g [lindex $values 1]]"\n' + needle)
        tcl, report = args.out / f'{name}.tcl', args.out / f'{name}.rpt'
        tcl.write_text(text)
        with report.open('w') as stream:
            subprocess.run([str(config.OPENSTA), '-no_init', '-exit', str(tcl)],
                           stdout=stream, stderr=subprocess.STDOUT, check=True)
        rows = dict(re.findall(r'^AUDIT_LEAF (\S+) (\S+)$', report.read_text(), re.M))
        if len(rows) != record['full']['leaf_count']:
            raise ValueError('per-leaf diagnostic is incomplete')
        return {key: float(value) for key, value in rows.items()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        full, *bins = executor.map(measure, ['full', *[f'bin-{i}' for i in range(8)]])
    durations = record['grid']['durations_s']
    rows = []
    for cell, power in full.items():
        weighted = sum(bin_[cell] * duration for bin_, duration in zip(bins, durations)) / sum(durations)
        rows.append({'cell': cell, 'full_w': power, 'weighted_w': weighted,
                     'difference_w': weighted - power, 'bins_w': [b[cell] for b in bins]})
    rows.sort(key=lambda r: abs(r['difference_w']), reverse=True)
    (args.out / 'largest_differences.json').write_text(json.dumps(rows[:50], indent=2) + '\n')
    print(json.dumps({'cells': len(rows), 'largest': rows[:3]}), flush=True)


if __name__ == '__main__':
    main()
