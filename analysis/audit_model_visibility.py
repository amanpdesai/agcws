"""Offline visibility audit of the published all-bin pilot and migration smoke."""

import argparse
import gzip
import hashlib
import json
import random
import tarfile
from pathlib import Path

from jsonschema import ValidationError

from agcws.pipeline.backends import backend
from agcws.pipeline.ibex.program import canonical
from agcws.pipeline.metrics import key
from agcws.pipeline.provider_schema import provenance


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_bundle(path):
    bundle = json.loads(gzip.decompress(path.read_bytes()))
    for name, item in bundle.items():
        if digest(item['text'].encode()) != item['sha256']:
            raise ValueError(f'archive member checksum mismatch: {name}')
    return {name: json.loads(item['text']) for name, item in bundle.items()}


def check_history(payload, history):
    by_slot = {t['slot']: t for t in history}
    for row in payload['history']:
        if row['slot'] not in by_slot:
            raise ValueError('nonprior or cross-cell history slot')
        for name, value in row.items():
            if by_slot[row['slot']].get(name) != value:
                raise ValueError(f'history differs: {row["slot"]}/{name}')
    # Independently verify the measurable direction component of notebook notes.
    for note in payload.get('experiment_notebook', []):
        trial = by_slot[note['slot']]
        if note['prediction'] != trial.get('prediction'):
            raise ValueError('notebook prediction differs')
        if note['scorable']:
            reference = by_slot[note['prediction']['reference_slot']]
            if reference['slot'] >= trial['slot']:
                raise ValueError('notebook uses a future reference')
            delta = [(a-b)/payload['goal']['scale']
                     for a, b in zip(trial['rates'], reference['rates'], strict=True)]
            directions = [0 if abs(v) <= .01 else 1 if v > 0 else -1 for v in delta]
            if delta != note['normalized_delta'] or directions != note['observed_directions']:
                raise ValueError('notebook measured delta differs')


def check_goal(goal, spec, target):
    expected = {'profile', 'scale', 'tolerance', 'success_metric', 'acceptance'}
    if set(goal) != expected:
        raise ValueError('unexpected goal fields')
    if (goal['profile'] != spec['targets'][target] or goal['scale'] != spec['scale'] or
            goal['tolerance'] != spec['tolerance'] or goal['success_metric'] != 'max-bin'):
        raise ValueError('goal differs from frozen task')
    if goal['acceptance'] != (
        'Every bin must satisfy abs(achieved-target)/scale <= tolerance. '
        'RMSE remains the ranking score; it is not sufficient for success. '
        'Use signed per-bin residuals to correct the worst interval.'
    ):
        raise ValueError('acceptance instruction differs')


def program_shape(program):
    """Diagnostic only: same grammar shape is not evidence of copying."""
    return [[op['op'] for op in segment['body']] for segment in program['segments']]


def audit_pilot(repo):
    archive = repo / 'results/ibex/maxbin-pilot-v1/evidence.json.gz'
    records = load_bundle(archive)
    manifest = records['manifest.json']
    spec = manifest['spec']
    design = backend(spec['domain'])
    if manifest['schema'] != design.schema(spec['batch_size']):
        raise ValueError('provider schema differs from generic schema')
    # Refuse to claim historical reconstruction with changed context/compiler code.
    checked_sources = ['backends.py', 'ibex/context.py', 'ibex/prompt.py',
                       'ibex/notebook.py', 'ibex/program.py', 'ibex/contract.py',
                       'ibex/native_schema.py']
    for name in checked_sources:
        path = Path('src/agcws/pipeline') / name
        if digest((repo/path).read_bytes()) != manifest['sources'][str(path)]:
            raise ValueError(f'historical reconstruction source changed: {path}')
    witness_path = repo / 'results/ibex/model-witnesses-v1/evidence/evidence-000.tar.gz'
    witnesses = {}
    with tarfile.open(witness_path) as tar:
        for member in tar:
            if member.isfile() and member.name.endswith('/program.json.gz'):
                program = json.loads(gzip.decompress(tar.extractfile(member).read()))
                witnesses[key(canonical(program))] = program
    if not witnesses:
        raise ValueError('empty witness inventory')
    counts = dict(cells=0, payloads=0, history_rows=0, notebook_notes=0,
                  responses_decoded=0, trials=0, cache_records_checked=0,
                  initialization_programs=0)
    exact, structural = [], []
    shapes = {key(program_shape(p)) for p in witnesses.values()}
    witness_hits_in_payload = []
    for target in spec['targets']:
        for seed in spec['seeds']:
            initial = None
            for arm in spec['policies']:
                counts['cells'] += 1
                prefix = f'panel/{target}/{seed}/{arm}/batches/'
                batches = sorted({name.split('/input.json')[0] for name in records
                                  if name.startswith(prefix) and name.endswith('/input.json')} |
                                 {name.rsplit('/', 1)[0] for name in records
                                  if name.startswith(prefix) and name.endswith('/trials.json')})
                history = []
                for batch in batches:
                    inp = records.get(batch+'/input.json')
                    if inp is not None:
                        payload = json.loads(inp['payload'])
                        check_history(payload, history)
                        expected = design.payload(history, payload['goal'], payload['batch_size'])
                        if expected != inp['payload']:
                            raise ValueError(f'payload byte reconstruction differs: {batch}')
                        goal = payload['goal']
                        check_goal(goal, spec, target)
                        counts['payloads'] += 1
                        counts['history_rows'] += len(payload['history'])
                        counts['notebook_notes'] += len(payload['experiment_notebook'])
                        for row in payload['history']:
                            if row['program'] is not None:
                                try:
                                    if key(canonical(row['program'])) in witnesses:
                                        witness_hits_in_payload.append([batch, row['slot']])
                                except (ValueError, ValidationError):
                                    if row['valid']:
                                        raise ValueError('valid history contains an invalid program') from None
                        response = records.get(batch+'/response.json')
                        if response:
                            if response['identity'] != inp['identity']:
                                raise ValueError('response from another request')
                            if response['schema_provenance'] != provenance(manifest['schema']):
                                raise ValueError('response schema provenance differs')
                            decoded = design.decode(response['raw_text'], payload['batch_size'])
                            if decoded != records[batch+'/decoded.json']:
                                raise ValueError('provider output/decoded mismatch')
                            for proposal, parsed in zip(records[batch+'/proposals.json'], decoded['slots'], strict=True):
                                if proposal['program'] != parsed['submitted']:
                                    raise ValueError('program replaced after model response')
                            counts['responses_decoded'] += 1
                    trials = records.get(batch+'/trials.json', [])
                    if trials:
                        proposals = records[batch+'/proposals.json']
                        if len(proposals) != len(trials) or any(
                            any(trial.get(k) != v for k, v in proposal.items())
                            for trial, proposal in zip(trials, proposals, strict=True)
                        ):
                            raise ValueError('evaluated proposal differs from submitted proposal')
                    if trials and not history:
                        programs = [t['program'] for t in trials]
                        rng = random.Random(seed)
                        if programs != [design.random(rng) for _ in programs]:
                            raise ValueError('initialization is not seed-only random')
                        if initial is not None and programs != initial:
                            raise ValueError('unequal shared initialization')
                        initial = programs
                        counts['initialization_programs'] += len(programs)
                    for trial in trials:
                        if trial['slot'] != len(history)+1:
                            raise ValueError('noncontiguous history')
                        if trial.get('cache_id'):
                            program = canonical(trial['program'])
                            if trial['cache_id'] != key({'program': program, 'measurement': manifest['measurement_fingerprint']}):
                                raise ValueError('cache identity mismatch')
                            cache = records['cache/'+trial['cache_id']+'/result.json']
                            if trial['valid'] and trial['rates'] != cache['profile']['window_rates']:
                                raise ValueError('trial rates not from own cached measurement')
                            for field in ('execution', 'feedback', 'allocation'):
                                if trial.get(field) != cache.get(field):
                                    raise ValueError(f'feedback differs from cache: {field}')
                            counts['cache_records_checked'] += 1
                            identity = [target, seed, arm, trial['slot']]
                            if key(program) in witnesses:
                                exact.append(identity)
                            if key(program_shape(program)) in shapes:
                                structural.append(identity)
                        history.append(trial)
                        counts['trials'] += 1
    return {'archive_sha256': digest(archive.read_bytes()),
            'witness_archive_sha256': digest(witness_path.read_bytes()),
            'witness_programs_compared': len(witnesses), 'counts': counts,
            'exact_witness_matches': exact, 'witness_matches_in_history': witness_hits_in_payload,
            'same_opcode_shape_matches': structural,
            'shape_match_interpretation': 'Descriptive, not a leakage test; shared DSL admits common shapes.',
            'reconstruction_sources': checked_sources}


def audit_migration(repo):
    root = repo/'out/gemini3-migration-smoke-v1'
    protocol = json.loads((root/'protocol.json').read_text())
    manifest = protocol['measurement_manifest']
    design = backend('aes-temporal')
    witness_path = repo/'results/aes/witness-refinement-v3/evidence-000.tar.gz'
    witnesses = {}
    with tarfile.open(witness_path) as tar:
        for member in tar:
            if member.isfile() and member.name.endswith('/program.json.gz'):
                program = json.loads(gzip.decompress(tar.extractfile(member).read()))
                witnesses.setdefault(key(design.canonical(program)), []).append(member.name)
    if not witnesses:
        raise ValueError('empty AES witness inventory')
    report = []
    for model, *_ in protocol['models']:
        history = []
        for turn in range(protocol['rounds']):
            directory = root/model/str(turn)
            payload = json.loads((directory/'input.json').read_text())
            row = json.loads((directory/'record.json').read_text())
            if json.loads(design.payload(history, payload['goal'], 1)) != payload:
                raise ValueError('migration payload reconstruction differs')
            if payload['goal']['target_rates'] != manifest['target_rates']:
                raise ValueError('migration goal differs')
            if payload['goal'] != {
                'target_rates': manifest['target_rates'], 'scale': manifest['scale'],
                'success': 'Every absolute normalized bin residual must be <= 0.05'
            }:
                raise ValueError('unexpected migration goal content')
            response = json.loads((directory/'response.json').read_text())
            text = ''.join(p.get('text', '') for c in response['candidates']
                           for p in c['content']['parts'] if not p.get('thought'))
            program = design.decode(text, 1)['slots'][0]['submitted']
            trial = row['trial']
            if trial['canonical_program'] != design.canonical(program):
                raise ValueError('migration evaluated different program')
            cache = json.loads((directory/'cache'/trial['cache_id']/'result.json').read_text())
            if trial['rates'] != cache['rates']:
                raise ValueError('migration rates differ from cache')
            report.append({'model': model, 'turn': turn, 'history_rows': len(history),
                           'payload_sha256': digest((directory/'input.json').read_bytes()),
                           'response_sha256': digest((directory/'response.json').read_bytes()),
                           'cache_hit': trial['cache_hit'],
                           'canonical_witness_matches': witnesses.get(key(trial['canonical_program']), [])})
            history.append({**trial, 'slot': turn, 'program': program})
    return {'witness_archive_sha256': digest(witness_path.read_bytes()),
            'witness_programs_compared': len(witnesses), 'calls': report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    result = {'scope': 'offline recorded-input and dataflow audit; no API calls or resimulation',
              'pilot': audit_pilot(repo), 'migration': audit_migration(repo),
              'limits': ['Not an independent waveform or binary-integrity audit.',
                         'Witness comparison covers 216 Ibex mixture candidates and 27 AES refinement programs, not every historical bank.',
                         'Shared grammar and hardware hints can make tasks easy without leaking answers.',
                         'Historical and future studies are not automatically certified.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
