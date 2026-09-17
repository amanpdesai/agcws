"""Read-only removal eligibility audit; never deletes files or starts experiments."""

import argparse
import concurrent.futures
import gzip
import hashlib
import json
import os
import subprocess
import tarfile
from pathlib import Path

from agcws.pipeline.evidence import verify

PAIRS = {
    'redmule-witness-v1-development': 'redmule/target-qualification-v1/development',
    'redmule-witness-v1-confirmation': 'redmule/target-qualification-v1/confirmation',
    'mesh-witness-v1-development': 'mesh/target-qualification-v1/development',
    'mesh-witness-v1-confirmation': 'mesh/target-qualification-v1/confirmation',
    'redmule-witness-refinement-v4': 'redmule/witness-refinement-v4',
    'redmule-bank-smoke-v4': 'redmule/bank-smoke-v4',
    'redmule-long-bin-witness-v1': 'redmule/long-bin-witness-v1',
    'redmule-operand-probe-v1': 'redmule/operand-probe-v1/evidence',
    'redmule-coarse-timing-v1': 'redmule/coarse-timing-v1/evidence',
    'redmule-pulse-witness-v2': 'redmule/pulse-witness-v2',
    'redmule-pulse-witness-v3': 'redmule/pulse-witness-v3',
    'redmule-long-calibration-v1': 'redmule/long-window-v1/calibration/evidence',
    'redmule-long-calibration-v4': 'redmule/calibration-replay-v4',
    'redmule-runtime-replay-v5': 'redmule/runtime-replay-v5',
    'mesh-bank-smoke-v3': 'mesh/bank-smoke-v3/evidence',
    'mesh-bank-smoke-v4': 'mesh/bank-smoke-v4',
    'ibex-model-witnesses-v1': 'ibex/model-witnesses-v1/evidence',
    'aes-schedule-witness-refinement-v3-restored': 'aes/witness-refinement-v3',
    'phase-ga-robustness-v1-restored': 'phase_ga_robustness_v1',
}

PROTECTED = {
    'baselines-model-v1': 'current full baseline panel, not yet published/archived',
    'baselines-maxbin-v1': 'retained compressed waveforms and recovery receipts',
    'retired-baselines-maxbin-v1': 'historical compact archive master copies',
    'phase-ga-robustness-v1': 'simulator binary referenced by frozen study configs',
    'redmule-dependencies-v2': 'configured generated RTL dependencies',
    'tools': 'configured OpenSTA installation and paper tool',
    '.cache': 'shared compilation cache; keep during runs',
    '.maintenance': 'recovery indexes and deletion journals',
    'trace-objects': 'compressed waveform store backing recovery indexes',
    'gemini3-migration-smoke-v1': 'full provider-response evidence not portably archived',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_pair(repo, name, archive_name):
    root, archive = repo/'out'/name, repo/'results'/archive_name
    if not (archive/'evidence.pack.json.gz').exists():
        return {'status': 'keep', 'reason': 'expected archive not present at checked path'}
    verify(archive)
    meta = json.loads(gzip.decompress((archive/'evidence.pack.json.gz').read_bytes()))
    covered = set()
    differences = []
    for shard in meta['shards']:
        with tarfile.open(archive/shard, 'r|gz') as tar:
            for member in tar:
                if not member.name.endswith('.gz'):
                    continue
                name_in_run = member.name[:-3]
                path = root/name_in_run
                if not path.exists():
                    continue
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f'nonregular source: {path}')
                data = gzip.decompress(tar.extractfile(member).read())
                if sha(data) != sha(path.read_bytes()):
                    differences.append(name_in_run)
                else:
                    covered.add(name_in_run)
    if 'manifest.json' not in covered:
        return {'status': 'keep', 'reason': 'archive does not match original manifest'}
    missing = []
    symlinks = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        for entry in [*dirs, *files]:
            if (Path(directory)/entry).is_symlink():
                symlinks.append(str((Path(directory)/entry).relative_to(root)))
        for filename in files:
            path = Path(directory)/filename
            relative = path.relative_to(root)
            if '.cache' in relative.parts or 'toolchain' in relative.parts:
                continue
            if path.suffix in ('.json', '.S') and str(relative) not in covered:
                missing.append(str(relative))
    reason = ('verified compact archive; waveform/build/diagnostic scratch can be discarded; '
              'waveforms would require regeneration')
    if missing or differences or symlinks:
        reason = 'archive coverage gap, changed records, or symlinks; keep pending review'
    return {'status': 'keep' if missing or differences or symlinks else 'remove',
            'reason': reason, 'archive': str(archive.relative_to(repo)),
            'archive_index_sha256': sha((archive/'evidence.pack.json.gz').read_bytes()),
            'verified_raw_files': len(covered), 'unarchived_records': missing,
            'different_records': differences, 'symlinks': symlinks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    roots = sorted((repo/'out').iterdir())
    rows = {p.name: {'path': str(p.relative_to(repo)), 'status': 'keep',
                    'reason': PROTECTED.get(p.name, 'archive/dependency coverage not established')}
            for p in roots}
    for p in roots:
        if p.is_dir() and not p.is_symlink() and not any(p.iterdir()) and p.name not in PROTECTED:
            rows[p.name].update(status='remove', reason='empty directory')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(check_pair, repo, name, archive): name
                   for name, archive in PAIRS.items() if name in rows}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            rows[name].update(future.result())
            print(name, rows[name]['status'], rows[name]['reason'], flush=True)
    sizes = subprocess.check_output(['du', '-B1', '--max-depth=1', str(repo/'out')], text=True)
    for line in sizes.splitlines():
        size, name = line.split('\t', 1)
        if Path(name).name in rows:
            rows[Path(name).name]['allocated_bytes'] = int(size)
    for p in roots:
        if p.is_file() and not p.is_symlink():
            rows[p.name]['allocated_bytes'] = p.stat().st_blocks*512
    args.output.mkdir(parents=True, exist_ok=True)
    for status in ('keep', 'remove'):
        (args.output/f'{status}.txt').write_text(''.join(
            row['path']+'\n' for row in rows.values() if row['status'] == status))
    (args.output/'inventory.json').write_text(json.dumps(list(rows.values()), indent=2)+'\n')
    print(json.dumps({status: {'entries': sum(r['status'] == status for r in rows.values()),
                              'bytes': sum(r.get('allocated_bytes', 0) for r in rows.values()
                                           if r['status'] == status)}
                      for status in ('keep', 'remove')}, indent=2))


if __name__ == '__main__':
    main()
