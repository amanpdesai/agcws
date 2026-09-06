"""Archive and independently reconcile the declared native-window panel."""
import argparse
import json
import math
import re
import shutil
from itertools import pairwise
from pathlib import Path

from analysis.matched_power import parse_report
from validation.aes_gls import sha


def nrmse(candidate, reference, durations):
    if not (len(candidate) == len(reference) == len(durations) == 8):
        raise ValueError('expected eight matched windows')
    if any(not math.isfinite(x) or x < 0 for x in [*candidate, *reference]):
        raise ValueError('invalid power')
    if any(not math.isfinite(d) or d <= 0 for d in durations):
        raise ValueError('invalid duration')
    denominator = math.fsum(d*r*r for d,r in zip(durations,reference))
    if denominator <= 0:
        raise ValueError('zero reference RMS')
    return math.sqrt(math.fsum(d*(p-r)**2 for d,p,r in zip(durations,candidate,reference))/denominator)


def checked_power(source, verify_inputs=True):
    data = json.loads((source/'power.json').read_text())
    for name, digest in data['artifact_sha256'].items():
        if sha(source/name) != digest:
            raise ValueError('changed report or invocation')
    if verify_inputs:
        for name, digest in data['inputs'].items():
            if sha(Path(name)) != digest:
                raise ValueError(f'changed measurement input: {name}')
    rows = [data['full'], *data['windows']]
    if [r['name'] for r in rows] != ['full', *[f'bin-{i}' for i in range(8)]]:
        raise ValueError('incomplete window set')
    grid = data['grid']
    cuts = grid['bounds_ticks']
    durations = grid['durations_ticks']
    if len(cuts) != 9 or durations != [b-a for a,b in pairwise(cuts)]:
        raise ValueError('invalid window durations')
    if cuts[0] != grid['span']['first_timestamp'] or cuts[-1] != grid['span']['last_timestamp']:
        raise ValueError('partition does not cover full waveform')
    for i,row in enumerate(rows):
        text = (source/f'{row["name"]}.rpt').read_text()
        parsed = parse_report(text)
        if any(row[key] != value for key,value in parsed.items()):
            raise ValueError('power JSON disagrees with native report')
        match = re.search(r'^LEAF_SWITCHING_SUM (\d+) ([0-9.eE+-]+)$',text,re.MULTILINE)
        if not match or row['leaf_count'] != int(match[1]) or row['leaf_switching_sum_w'] != float(match[2]):
            raise ValueError('leaf sum disagrees with report')
        begin, end = (cuts[0], cuts[-1]) if i == 0 else (cuts[i-1],cuts[i])
        if (row['begin_tick'],row['end_tick']) != (begin,end):
            raise ValueError('wrong measurement bounds')
        tcl = (source/f'{row["name"]}.tcl').read_text()
        if f'-begin_time {begin} -end_time {end} ' not in tcl:
            raise ValueError('native window not invoked')
        if (row['annotated_pins'],row['unannotated_pins'],row['leaf_count']) != (
                rows[0]['annotated_pins'],rows[0]['unannotated_pins'],rows[0]['leaf_count']):
            raise ValueError('coverage changed between windows')
    weighted = math.fsum(d*r['leaf_switching_sum_w'] for d,r in zip(durations,rows[1:]))/sum(durations)
    full = rows[0]['leaf_switching_sum_w']
    if not math.isclose(weighted,full,rel_tol=1e-5,abs_tol=1e-12) or not data['switching_additivity_pass']:
        raise ValueError('switching additivity failed')
    return data


def input_digest(data, path):
    matches = [digest for name,digest in data['inputs'].items() if Path(name).resolve() == path.resolve()]
    if len(matches) != 1:
        raise ValueError('missing/ambiguous recorded input')
    return matches[0]


def archive(root, out):
    selection = Path('results/structural_temporal_finalists_v1.json')
    cases = json.loads(selection.read_text())['cases']
    previous = Path('results/structural_temporal_finalist_validation_v1/validation.json')
    validation = json.loads(previous.read_text())
    if validation['selection_sha256'] != sha(selection) or len(cases) != 16:
        raise ValueError('changed finalist selection')
    sources, powers = {}, {}
    for case in cases:
        key = 'finalists/'+case['replay_id']
        sources[key] = root/'measurements'/key
    for design in ('aes','dma'):
        for target in ('random_300','random_301'):
            key = f'references/{design}/{target}'
            sources[key] = root/'measurements'/key
    for key, source in sources.items():
        powers[key] = checked_power(source)
    references = []
    for design in ('aes','dma'):
        for target in ('random_300','random_301'):
            key = f'references/{design}/{target}'
            power = powers[key]
            replay = root/key
            done = json.loads((replay/'completed.json').read_text())
            if sha(replay/'archive/comparison.json') != done['comparison_sha256']:
                raise ValueError('reference replay comparison changed')
            comparison = json.loads((replay/'archive/comparison.json').read_text())
            provenance_path = replay/'archive/gls_provenance.json'
            if sha(provenance_path) != comparison['artifact_sha256']['gls_provenance.json']:
                raise ValueError('reference provenance changed')
            provenance = json.loads(provenance_path.read_text())
            if input_digest(power,replay/'gls/activity.vcd') != provenance['waveform_sha256']:
                raise ValueError('reference GLS waveform differs from matched replay')
            references.append({'design':design,'target':target,'measurement':key,
                               'dynamic_power_w':[r['dynamic_power_w'] for r in power['windows']],
                               'replay':done})
    rows = []
    for case in cases:
        power = powers['finalists/'+case['replay_id']]
        reference = powers[f'references/{case["design"]}/{case["target"]}']
        if power['grid'] != reference['grid']:
            raise ValueError('candidate/reference grids differ')
        old = validation['unique_replays'][case['replay_id']]
        provenance_path = previous.parent/'replays'/case['replay_id']/'gls_provenance.json'
        if sha(provenance_path) != old['comparison']['artifact_sha256']['gls_provenance.json']:
            raise ValueError('finalist provenance changed')
        provenance = json.loads(provenance_path.read_text())
        gls_waveform = Path('out/structural-temporal-finalists-v1/replays')/case['replay_id']/'gls/activity.vcd'
        if input_digest(power,gls_waveform) != provenance['waveform_sha256']:
            raise ValueError('finalist waveform differs from matched replay')
        rtl = Path('out/structural-temporal-heldout-v1')/case['run']/'evaluations'/f'trial-{case["evaluation_index"]:05d}'
        if sha(rtl/'activity.json') != case['activity_profile']['provenance']['activity_sha256']:
            raise ValueError('finalist activity differs from selected trial')
        if input_digest(power,rtl/'activity.vcd') != json.loads((rtl/'activity.json').read_text())['waveform_sha256']:
            raise ValueError('finalist RTL waveform changed')
        if power['grid']['span'] != old['waveform_windows']['gls']:
            raise ValueError('finalist window changed')
        values = [r['dynamic_power_w'] for r in power['windows']]
        ref = [r['dynamic_power_w'] for r in reference['windows']]
        rows.append({**{k:case[k] for k in ('design','target','policy','seed','replay_id','proposal_source')},
                     'activity_error':case['loss'], 'dynamic_power_w':values,
                     'gate_nrmse':nrmse(values,ref,power['grid']['durations_s']),
                     'full_dynamic_power_w':power['full']['dynamic_power_w'],
                     'window_min_w':min(values),'window_max_w':max(values)})
    out.mkdir(parents=True,exist_ok=False)
    for key, source in sources.items():
        shutil.copytree(source,out/key)
    for entry in references:
        key = entry['measurement']
        shutil.copytree(root/key/'archive',out/key/'matched_replay')
        shutil.copy2(root/key/'completed.json',out/key/'completed.json')
    for name in ('validation/window_power.py','validation/window_grid.py',
                 'validation/window_matrix.py','validation/check_power_accumulation.py',
                 'validation/check_window_semantics.py','validation/reference_power.py',
                 'docs/WINDOWED_POWER_PROTOCOL.md'):
        destination = out/'executed_sources'/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(name,destination)
    precision = root/'precision-audit'
    shutil.copy2(precision/'audit.json',out/'precision_audit.json')
    diagnostics = {str(p.relative_to(precision)):sha(p) for p in sorted(precision.glob('*'))}
    result = {'scope':'Post-search descriptive gate-profile validation, not gate-guided search or new policy inference.',
              'selection_sha256':sha(selection),'prior_validation_sha256':sha(previous),
              'cases':rows,'references':references,'measurement_count':len(powers),
              'power_reports':len(powers)*9,'precision_diagnostic_sha256':diagnostics,
              'measurement_wall_clock_s':math.fsum(p['wall_clock_s'] for p in powers.values()),
              'limitations':['Selected seed-400 finalists and previously observed references, not general proxy validation.',
                             'Zero-delay functional cell models; no timing-induced glitches or signoff claims.',
                             'Gate NRMSE uses reference RMS; activity error uses its original fixed scale.'],
              'artifact_sha256':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path('out/window-power-v1'))
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    result = archive(args.root,args.out)
    print('WINDOW_ARCHIVE_VERIFIED',len(result['cases']),len(result['references']))
