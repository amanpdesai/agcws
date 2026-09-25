#!/usr/bin/env python3
"""Content-addressed compiler cache for the prepared RedMulE GLS recipe."""

import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from agcws.core.storage import read, write
from agcws.designs.aes.gls import sha


def identity(args, compiler, image):
    if args.count('-f') != 1 or '--binary' not in args:
        raise ValueError('cache only accepts the prepared GLS binary recipe')
    prepared = Path(args[args.index('-f') + 1]).parent
    manifest = read(prepared / 'preparation.json')
    closure = dict(manifest['sources'])
    closure.update({str(prepared / p): h for p, h in manifest['generated'].items()})
    for path, expected in closure.items():
        if sha(Path(path)) != expected:
            raise ValueError(f'compile source changed: {path}')
    normalized, files, i = [], {}, 0
    while i < len(args):
        token = args[i]
        if token in ('--Mdir', '-o', '-j'):
            i += 2
            continue
        path = Path(token)
        if path.is_file():
            digest = sha(path)
            files[str(path)] = digest
            normalized.append({'file': path.name, 'sha256': digest})
        else:
            normalized.append(token)
        i += 1
    return {'schema': 'redmule-gls-build-v1', 'image': image,
            'compiler_sha256': sha(Path(compiler)), 'closure': closure,
            'arguments': normalized}, files


def cached_compile(args, compiler, cache, image, jobs=2):
    if jobs < 1 or jobs > 4:
        raise ValueError('cached GLS compilation allows one to four jobs')
    recipe, files = identity(args, compiler, image)
    digest = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
    cache = Path(cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    destination = cache / digest
    with (cache / f'{digest}.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        hit = destination.exists()
        if not hit:
            # One build across keys as well as one writer per cache entry.
            with (cache / 'compile.lock').open('a') as admission:
                fcntl.flock(admission, fcntl.LOCK_EX)
                staging = Path(tempfile.mkdtemp(prefix=f'{digest}.build-', dir=cache))
                command = list(args)
                command[command.index('--Mdir') + 1] = str(staging / 'obj')
                command[command.index('-o') + 1] = str(staging / 'simulate')
                command[command.index('-j') + 1] = str(jobs)
                subprocess.run([compiler, *command], check=True)
                if identity(args, compiler, image)[0] != recipe:
                    raise ValueError('compile inputs changed during build')
                write(staging / 'receipt.json', {'identity': recipe,
                      'binary_sha256': sha(staging / 'simulate'), 'command': command})
                staging.rename(destination)
        receipt = read(destination / 'receipt.json')
        binary = destination / 'simulate'
        if receipt['identity'] != recipe or sha(binary) != receipt['binary_sha256']:
            raise ValueError('compiled simulator cache failed integrity check')
        output = Path(args[args.index('-o') + 1])
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(binary, output)
        record = {'schema': 'redmule-gls-cache-use-v1', 'key': digest, 'hit': hit,
                  'binary_sha256': receipt['binary_sha256'], 'inputs': files,
                  'cache_receipt_sha256': sha(destination / 'receipt.json')}
        write(output.parent / 'cache_receipt.json', record)
        print(json.dumps(record), flush=True)
        return record


def main():
    compiler = shutil.which(os.environ.get('AGCWS_REAL_VERILATOR', '/usr/bin/verilator'))
    if compiler is None:
        raise FileNotFoundError('real Verilator is unavailable')
    args = sys.argv[1:]
    if args == ['--version']:
        subprocess.run([compiler, '--version'], check=True)
        return
    cached_compile(args, compiler,
                   os.environ.get('AGCWS_GLS_BUILD_CACHE', 'out/.cache/redmule-gls'),
                   os.environ['AGCWS_GLS_IMAGE_ID'],
                   int(os.environ.get('AGCWS_REDMULE_GLS_JOBS', '2')))


if __name__ == '__main__':
    main()
