"""Read the final power inventory and its hash-bound validation evidence."""

import gzip
import hashlib
import json
from pathlib import Path

from agcws.evidence import catalog


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_bytes(root, entry, inputs=None):
    raw = catalog.safe_path(root, entry['path']).read_bytes()
    if digest(raw) != entry['sha256']:
        raise ValueError(f"power evidence hash mismatch: {entry['path']}")
    if inputs is not None:
        inputs[entry['path']] = entry['sha256']
    return raw


def unpack_record(row):
    raw = row['raw_measurement'].encode()
    if digest(raw) != row['receipt']['measurement_sha256']:
        raise ValueError('archived measurement hash mismatch')
    record = json.loads(raw)
    if record['activity'] != row['case'] or record['case_id'] != row['case']['id']:
        raise ValueError('archived selection mismatch')
    if record['plan_sha256'] != row['plan_sha256']:
        raise ValueError('archived plan mismatch')
    return record


def load(root, design, inputs=None):
    inputs = {} if inputs is None else inputs
    root = Path(root)
    index_raw = (root / 'results/index.json').read_bytes()
    inputs['results/index.json'] = digest(index_raw)
    entry = catalog.load(root)['designs'][design]
    raw = checked_bytes(root, {'path':entry['power'], 'sha256':entry['power_sha256']}, inputs)
    buckets = [json.loads(line) for line in gzip.decompress(raw).splitlines()]
    records = {}
    identities = set()
    for bucket in buckets:
        for row in bucket['records']:
            if row['status'] != 'measured':
                raise ValueError('final power inventory contains an unmeasured case')
            record = unpack_record(row)
            if 'plan_sha256' in bucket and record['plan_sha256'] != bucket['plan_sha256']:
                raise ValueError('archived bucket plan mismatch')
            identity = tuple(row['case'][k] for k in ('policy','target','seed'))
            if record['case_id'] in records or identity in identities:
                raise ValueError('duplicate power case')
            records[record['case_id']] = record
            identities.add(identity)
    if len(records) != 459:
        raise ValueError('incomplete final power inventory')
    for field in ('references', 'power_validation'):
        path = entry[field]
        data = checked_bytes(root, {'path':path, 'sha256':entry[field + '_sha256']}, inputs)
        proof = json.loads(data)
        for name, expected in proof['inputs'].items():
            checked_bytes(root, {'path':name, 'sha256':expected}, inputs)
        for key, item in proof.get('references', proof.get('entries', {})).items():
            case_id = item.get('case_id', key)
            matches = [r for b in buckets for r in b['records'] if r['case']['id'] == case_id]
            if len(matches) != 1 or matches[0]['receipt']['measurement_sha256'] != item['sha256']:
                raise ValueError('validation does not bind the final measurement')
            if field == 'references' and records[case_id]['activity']['target'] != key:
                raise ValueError('reference evidence names a different target')
            if 'original_sha256' in item:
                if records[case_id].get('revalidation', {}).get('source_sha256') != item['original_sha256']:
                    raise ValueError('clipping audit does not bind its original source')
    return buckets, records
