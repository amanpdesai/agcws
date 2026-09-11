"""One-off completed-study retention; never launch or alter an experiment."""

import concurrent.futures
import gzip
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from maintenance.clean_artifacts import active_references, fingerprint
from maintenance.find_delete import execute_find
from maintenance.trace_store import pack_file, verify_object


def main():
    root = REPO / 'out/nonflat-temporal-v1'
    archive = REPO / 'results/nonflat_temporal_v1'
    destination = REPO / 'out/cleanup-nonflat-20260911'
    if root.is_symlink() or root.resolve() != root:
        raise ValueError('unsafe scratch root')
    if active_references(REPO/'out', [root.name]):
        raise ValueError('active experiment')
    if not (archive/'complete.json').is_file() or not (root/'complete.json').is_file():
        raise ValueError('completed study required')
    if json.loads((archive/'summary.json').read_text())['slots'] != 4608:
        raise ValueError('unexpected completed study')
    protected, cells = set(), []
    for cell in sorted((archive/'panel').glob('*/*/*')):
        rows=[]
        for record in sorted(cell.glob('batches/*/trials.json.gz')):
            data=gzip.decompress(record.read_bytes())
            relative=record.relative_to(archive).with_suffix('')
            if data != (root/relative).read_bytes():
                raise ValueError(f'local/archive trial mismatch: {relative}')
            rows.extend(json.loads(data))
        if [r['slot'] for r in rows] != list(range(1,129)):
            raise ValueError('incomplete cell')
        best=min((r for r in rows if r['valid']),key=lambda r:(r['loss'],r['slot']))
        protected.add(best['cache_id'])
        cells.append({'cell':str(cell.relative_to(archive)), 'slot':best['slot'], 'cache_id':best['cache_id']})
    if len(cells)!=36:
        raise ValueError('expected 36 cells')
    for witness in json.loads((archive/'witnesses.json').read_text()):
        if witness.get('cache_id'): protected.add(witness['cache_id'])
    for target in json.loads((archive/'targets.json').read_text()):
        protected.add(target['witness_cache_id'])
    waves, logs = [], []
    for directory in sorted((root/'cache').iterdir()):
        if directory.is_symlink() or directory.name in protected:
            continue
        for path in directory.rglob('*'):
            if not path.is_file(): continue
            if path.resolve()!=path: raise ValueError('symlink inside selected cache')
            if path.suffix in ('.fst','.vcd','.saif'): waves.append(path)
            elif path.suffix=='.log' and path.stat().st_size>=1024*1024: logs.append(path)
    destination.mkdir(exist_ok=False)
    before={str(p):fingerprint(p) for p in [*waves,*logs]}
    allocated=sum(p.stat().st_blocks*512 for p in [*waves,*logs])
    plan={'cells':cells,'protected_cache_ids':sorted(protected), 'waveforms':[str(p) for p in waves],
          'logs':[str(p) for p in logs], 'fingerprints':before, 'allocated_bytes':allocated}
    (destination/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'waveforms_to_delete':len(waves),'logs_to_compress':len(logs),'allocated_bytes':allocated}),flush=True)
    objects=REPO/'out/trace-objects/sha256'
    def pack(path):
        return {'path':str(path.relative_to(REPO/'out')),**pack_file(path,objects)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        entries=list(pool.map(pack,logs))
    index={'entries':entries,'source':'completed non-flat study; logs only'}
    (destination/'logs.json').write_text(json.dumps(index,indent=2)+'\n')
    for entry in entries: verify_object(entry)
    for path in [*waves,*logs]:
        if fingerprint(path)!=before[str(path)]: raise ValueError('source changed')
    if active_references(REPO/'out',[root.name]): raise ValueError('run became active')
    deleted=execute_find([*waves,*logs],destination/'deleted.jsonl',destination/'paths.nul')
    compressed=sum(e['compressed_bytes'] for e in entries)
    result={'deleted_files':len(deleted),'deleted_waveforms':len(waves),'compressed_logs':len(logs),
            'protected_cache_ids':sorted(protected),'protected_cell_finalists':cells,
            'raw_allocated_bytes':allocated,'compressed_log_bytes':compressed,
            'net_bytes_reclaimed_approx':allocated-compressed,
            'plan_sha256':hashlib.sha256((destination/'plan.json').read_bytes()).hexdigest(),
            'logs_index_sha256':hashlib.sha256((destination/'logs.json').read_bytes()).hexdigest(),
            'recovery':'Logs restore via maintenance.trace_store with logs.json; deleted nonfinalist waveforms require replay. Programs, binary, measurements and finalist/witness caches retained.'}
    (destination/'complete.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
