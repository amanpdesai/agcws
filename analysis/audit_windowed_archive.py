"""Review compact window evidence without local tools or large waveforms."""
import argparse
import json
import math
from pathlib import Path

from analysis.windowed_finalists import checked_power, nrmse
from validation.aes_gls import sha


def audit(root):
    report = json.loads((root/'validation.json').read_text())
    for name,digest in report['artifact_sha256'].items():
        if sha(root/name) != digest:
            raise ValueError(f'changed artifact: {name}')
    selected = Path('results/structural_temporal_finalists_v1.json')
    if sha(selected) != report['selection_sha256']:
        raise ValueError('selection changed')
    cases = json.loads(selected.read_text())['cases']
    keys = ('design','target','policy','seed','replay_id','proposal_source')
    if [tuple(c[k] for k in keys) for c in cases] != [tuple(c[k] for k in keys) for c in report['cases']]:
        raise ValueError('finalist identities changed')
    if report['measurement_count'] != 20 or report['power_reports'] != 180 or len(report['references']) != 4:
        raise ValueError('incomplete matrix')
    powers = {}
    for path in sorted(root.glob('**/power.json')):
        if 'matched_replay' in path.parts:
            continue
        power = checked_power(path.parent,verify_inputs=False)
        grid = power['grid']
        if not math.isclose(grid['clock_period_ticks']*grid['span']['timescale_s'],10e-9,rel_tol=1e-12):
            raise ValueError('clock differs from declared 10 ns constraint')
        if grid['durations_s'] != [d*grid['span']['timescale_s'] for d in grid['durations_ticks']]:
            raise ValueError('duration unit conversion differs')
        for name in ('validation/window_power.py','validation/window_grid.py','docs/WINDOWED_POWER_PROTOCOL.md'):
            suffix = Path(name).parts
            digests = [v for k,v in power['inputs'].items() if Path(k).parts[-len(suffix):] == suffix]
            if digests != [sha(root/'executed_sources'/name)]:
                raise ValueError('executed measurement source snapshot changed')
        powers[str(path.parent.relative_to(root))] = power
    if len(powers) != 20:
        raise ValueError('missing measurement files')
    for row,case in zip(report['cases'],cases):
        power = powers['finalists/'+row['replay_id']]
        reference = powers[f'references/{row["design"]}/{row["target"]}']
        values = [r['dynamic_power_w'] for r in power['windows']]
        ref = [r['dynamic_power_w'] for r in reference['windows']]
        if power['grid'] != reference['grid'] or row['dynamic_power_w'] != values:
            raise ValueError('profile/window changed')
        error = nrmse(values,ref,power['grid']['durations_s'])
        if error != row['gate_nrmse'] or row['activity_error'] != case['loss']:
            raise ValueError('error changed')
    return {'verified_finalists':16,'verified_references':4,'verified_reports':180,
            'archive_sha256':sha(root/'validation.json'),
            'scope':'Compact arithmetic/hash reconciliation; does not independently rerun GLS or OpenSTA.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,default=Path('results/windowed_power_v1'))
    args = parser.parse_args()
    print(json.dumps(audit(args.archive),indent=2))
