"""Archive compact, same-program/window AES GLS evidence without waveforms."""
import argparse
import json
import shutil
from pathlib import Path

from agcws.designs.aes.gls import PARAMETERS, sha
from agcws.evaluation.power.parse import parse_report


def archive(rtl, gls, synthesis, destination):
    provenance = json.loads((gls / 'provenance.json').read_text())
    mapped = json.loads((synthesis / 'manifest.json').read_text())
    left = json.loads((rtl / 'activity.json').read_text())
    right = json.loads((gls / 'activity.json').read_text())
    if not (sha(rtl / 'program.txt') == sha(gls / 'program.txt') == provenance['program_sha256']):
        raise ValueError('different transaction programs')
    if not (left['clock_edges'] == right['clock_edges'] == provenance['clock_edges']):
        raise ValueError('different observation windows')
    if mapped['parameters'] != PARAMETERS or provenance['parameters'] != PARAMETERS:
        raise ValueError('configuration mismatch')
    if sha(synthesis / 'mapped.v') != mapped['netlist_sha256']:
        raise ValueError('netlist checksum mismatch')
    report_path = gls / 'power/power.rpt'
    power = parse_report(report_path.read_text())
    result = {'scope': 'One reference-checked matched AES replay; not a correlation or agent-performance result.',
              'parameters': PARAMETERS, 'clock_edges': left['clock_edges'],
              'blocks_checked': provenance['blocks_checked'], 'program_sha256': provenance['program_sha256'],
              **power,
              'limitation': 'Functional zero-delay gates; no timing-induced glitch or signoff claim.'}
    for tier, activity in [('rtl', left), ('gls', right)]:
        samples = activity['per_cycle_toggles']
        edges = activity['clock_edges']
        if len(samples) != edges:
            raise ValueError('incomplete cycle series')
        result[tier] = {'total_transitions': activity['total_transitions'],
                        'window_rates': [sum(samples[i*edges//8:(i+1)*edges//8]) /
                                         ((i+1)*edges//8-i*edges//8) for i in range(8)]}
    files = {'workload.json': rtl / 'workload.json', 'program.txt': rtl / 'program.txt',
             'gls_provenance.json': gls / 'provenance.json', 'synthesis_manifest.json': synthesis / 'manifest.json',
             'power.rpt': report_path, 'gls_run.log': gls / 'run.log', 'rtl_run.log': rtl / 'run.log'}
    result['artifact_sha256'] = {name: sha(path) for name, path in files.items()}
    destination.mkdir(parents=True, exist_ok=False)
    for name, path in files.items():
        shutil.copy2(path, destination / name)
    (destination / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    for name in ('rtl', 'gls', 'synthesis', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args(argv)
    result = archive(args.rtl, args.gls, args.synthesis, args.out)
    print(json.dumps({k: result[k] for k in ('clock_edges', 'blocks_checked', 'annotated_pins', 'unannotated_pins')}))


if __name__ == '__main__':
    main()
