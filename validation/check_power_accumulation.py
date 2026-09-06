"""Independently sum native per-leaf powers to audit float accumulation."""
import argparse
import json
import math
import subprocess
from pathlib import Path

from agcws import config


def audit(source, out):
    out.mkdir(parents=True, exist_ok=False)
    values = []
    for name in ['full', *[f'bin-{i}' for i in range(8)]]:
        tcl = out / f'{name}.tcl'
        tcl.write_text((source / f'{name}.tcl').read_text() + '\n'
                       'foreach inst [sta::network_leaf_instances] {\n'
                       ' puts "LEAF [sta::get_full_name $inst] [sta::instance_power $inst [sta::cmd_scene]]"\n'
                       '}\n')
        report = out / f'{name}.rpt'
        with report.open('w') as log:
            subprocess.run([str(config.OPENSTA), '-no_init', '-exit', str(tcl)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        rows = [line.split()[-4:] for line in report.read_text().splitlines() if line.startswith('LEAF ')]
        if not rows:
            raise ValueError('no leaf powers')
        values.append({'name': name, 'leaves': len(rows),
                       'internal': math.fsum(float(r[0]) for r in rows),
                       'switching': math.fsum(float(r[1]) for r in rows)})
    durations = json.loads((source / 'power.json').read_text())['grid']['durations_ticks']
    weighted = math.fsum(d*r['switching'] for d, r in zip(durations, values[1:])) / sum(durations)
    result = {'rows': values, 'weighted_switching': weighted,
              'relative_difference': (weighted-values[0]['switching'])/values[0]['switching']}
    (out/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    audit(args.source, args.out)
