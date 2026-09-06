"""Archive matched DMA completion, timing and gate-power evidence."""
import argparse
import json
import shutil
from pathlib import Path

from analysis.matched_power import parse_report
from validation.aes_gls import sha


def archive(rtl, gls, synthesis, destination):
    provenance = json.loads((gls / 'provenance.json').read_text())
    original = json.loads((rtl / 'sim_build/observed.json').read_text())
    observed = json.loads((gls / 'sim_build/observed.json').read_text())
    left = json.loads((rtl / 'activity.json').read_text())
    right = json.loads((gls / 'activity.json').read_text())
    mapped = json.loads((synthesis / 'manifest.json').read_text())
    if original != observed or provenance['observed'] != observed:
        raise ValueError('completion/timing observations differ')
    if not (left['clock_edges'] == right['clock_edges'] == observed['observation_cycles']):
        raise ValueError('measurement windows differ')
    if provenance['inputs'][str((rtl / 'workload.json').resolve())] != sha(rtl / 'workload.json'):
        raise ValueError('workload checksum mismatch')
    if provenance['inputs'][str((synthesis / 'mapped.v').resolve())] != mapped['netlist_sha256']:
        raise ValueError('netlist checksum mismatch')
    result = {'scope': 'One reference-checked matched DMA replay; not a correlation or agent-performance result.',
              'observed': observed, 'clock_edges': left['clock_edges'],
              **parse_report((gls / 'power/power.rpt').read_text()),
              'limitation': 'Functional zero-delay gates; no timing-induced glitch or signoff claim.'}
    for tier, activity in [('rtl', left), ('gls', right)]:
        samples = activity['per_cycle_toggles']
        edges = activity['clock_edges']
        if len(samples) != edges:
            raise ValueError('incomplete cycle series')
        result[tier] = {'total_transitions': activity['total_transitions'],
                        'window_rates': [sum(samples[i*edges//8:(i+1)*edges//8]) /
                                         ((i+1)*edges//8-i*edges//8) for i in range(8)]}
    files = {'workload.json': rtl / 'workload.json', 'observed.json': gls / 'sim_build/observed.json',
             'gls_provenance.json': gls / 'provenance.json', 'synthesis_manifest.json': synthesis / 'manifest.json',
             'power.rpt': gls / 'power/power.rpt', 'gls_driver.log': gls / 'driver.log'}
    result['artifact_sha256'] = {name: sha(path) for name, path in files.items()}
    destination.mkdir(parents=True, exist_ok=False)
    for name, path in files.items():
        shutil.copy2(path, destination / name)
    (destination / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    for name in ('rtl', 'gls', 'synthesis', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = archive(args.rtl, args.gls, args.synthesis, args.out)
    print(json.dumps({k: result[k] for k in ('clock_edges', 'annotated_pins', 'unannotated_pins')}))


if __name__ == '__main__':
    main()
