"""Restore exact historical measurement sources without editing frozen runs."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from agcws.core.provenance import file_sha256
from agcws.evaluation.power.frozen import verify_sources


def recover_blob(repository, name, expected):
    commits = subprocess.check_output(
        ['git', '-C', str(repository), 'log', '--all', '--format=%H', '--', name], text=True).splitlines()
    for commit in commits:
        blob = subprocess.run(['git', '-C', str(repository), 'show', f'{commit}:{name}'],
                              capture_output=True)
        if blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == expected:
            return blob.stdout, commit
    raise ValueError(f'No exact historical source found: {name}')


def prepare(manifest_paths, template, out, repository):
    if out.exists():
        raise ValueError('Runtime destination must be new')
    manifests = [json.loads(p.read_text()) for p in manifest_paths]
    sources = {}
    for manifest in manifests:
        for name, expected in manifest['sources'].items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'unsafe source path: {name}')
            if name in sources and sources[name] != expected:
                raise ValueError(f'manifests require different source versions: {name}')
            sources[name] = expected
    replacements, origins = {}, {}
    for name, expected in sources.items():
        if Path(name).parts[0] == '.dependencies':
            continue
        original = template / name
        if original.is_file() and file_sha256(original) == expected:
            continue
        replacements[name], origins[name] = recover_blob(repository, name, expected)
    shutil.copytree(template, out, ignore=shutil.ignore_patterns(
        'out', '.env', '.dependencies', '__pycache__', '*.pyc', '.git'))
    for name, data in replacements.items():
        destination = out / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    (out / 'out').mkdir()
    (out / '.dependencies').mkdir()
    for manifest in manifests:
        verify_sources(manifest, out)
    receipt = {'version': 'frozen-power-runtime-v1', 'template': str(template.resolve()),
               'runtime': str(out.resolve()), 'source_count': len(sources),
               'manifest_sha256': {str(p): file_sha256(p) for p in manifest_paths},
               'git_restorations': {name: {'commit': commit, 'sha256': sources[name]}
                                    for name, commit in origins.items()},
               'sources_verified': True, 'paid_calls': 0,
               'limitation': 'Source snapshot, not a standalone container or credentials backup'}
    (out / 'power-runtime-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifests', type=Path, nargs='+', required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(prepare(args.manifests, args.template, args.out, Path.cwd()), indent=2))


if __name__ == '__main__':
    main()
