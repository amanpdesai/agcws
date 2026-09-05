"""Plan and audit removal of regenerable waveforms from explicit retired runs."""
import argparse
import json
import os
import stat
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUFFIXES = {'.vcd', '.fst', '.saif'}


def target_path(root, name):
    if Path(name).name != name or name.startswith('.') or name in {'', 'retired'}:
        raise ValueError(f'not an explicit top-level run: {name}')
    path = root / name
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f'not a real run directory: {path}')
    if 'heldout' in name or 'synthesis' in name or 'cache' in name:
        raise ValueError(f'protected evaluation/build directory: {name}')
    return path


def active_references(root, targets):
    found = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            command = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            if 'clean_artifacts.py' in command:
                continue
            cwd = (proc / 'cwd').resolve()
        except (OSError, PermissionError):
            continue
        for name in targets:
            path = root / name
            if str(path) in command or f'out/{name}' in command or cwd == path or path in cwd.parents:
                found.append((proc.name, name))
    return found


def fingerprint(path):
    value = path.lstat()
    if not stat.S_ISREG(value.st_mode):
        raise ValueError(f'not a regular file: {path}')
    return [value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns]


def waveform_files(target):
    for directory, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink()]
        for name in files:
            path = Path(directory) / name
            if path.suffix.lower() in SUFFIXES and not path.is_symlink():
                yield path


def checked_file(root, entry, targets):
    relative = Path(entry['path'])
    if relative.is_absolute() or '..' in relative.parts or relative.parts[0] not in targets:
        raise ValueError('cleanup entry escapes selected runs')
    path = root / relative
    if path.suffix.lower() not in SUFFIXES or path.resolve() != path:
        raise ValueError('cleanup entry is not an ordinary waveform path')
    if fingerprint(path) != entry['fingerprint']:
        raise ValueError(f'file changed since planning: {path}')
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', nargs='+')
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--retire', action='store_true', help='move cleaned runs under out/retired')
    parser.add_argument('--skip-unwritable', action='store_true', help='emit a separate plan for root-owned traces')
    args = parser.parse_args()
    root = REPO / 'out'
    if root.is_symlink():
        raise ValueError('out must not be a symlink')
    if args.apply:
        plan = json.loads(args.plan.read_text())
        if plan['root'] != str(root):
            raise ValueError('plan belongs to a different artifact root')
        targets = plan['targets']
    else:
        targets = args.targets or []
        if not targets or len(targets) != len(set(targets)):
            raise ValueError('explicit unique targets are required')
    paths = [target_path(root, name) for name in targets]
    active = active_references(root, targets)
    if active:
        raise ValueError(f'active process references selected runs: {active}')
    tracked = subprocess.check_output(['git', 'ls-files', '-z', 'out'], cwd=REPO).decode().split('\0')
    if args.apply:
        if args.retire and any((root / 'retired' / name).exists() for name in targets):
            raise ValueError('retirement destination already exists')
        selected, deferred = [], []
        for entry in plan['files']:
            path = checked_file(root, entry, targets)
            if not os.access(path.parent, os.W_OK):
                if not args.skip_unwritable:
                    raise PermissionError(f'cannot remove waveform from {path.parent}')
                deferred.append(entry)
            else:
                selected.append(entry)
            if str(path.relative_to(REPO)) in tracked:
                raise ValueError('refusing to delete tracked waveform')
        deferred_targets = sorted({Path(e['path']).parts[0] for e in deferred})
        if deferred:
            remaining = {**plan, 'targets': deferred_targets, 'files': deferred,
                         'allocated_bytes': sum((root / e['path']).stat().st_blocks * 512 for e in deferred)}
            with args.plan.with_suffix('.remaining.json').open('x') as output:
                output.write(json.dumps(remaining, indent=2) + '\n')
        allocated = sum((root / e['path']).stat().st_blocks * 512 for e in selected)
        log_path = args.plan.with_suffix('.deleted.jsonl')
        with log_path.open('x') as log:
            for entry in selected:
                checked_file(root, entry, targets).unlink()
                log.write(json.dumps(entry) + '\n')
        if args.retire:
            (root / 'retired').mkdir(exist_ok=True)
            for path in paths:
                if path.name not in deferred_targets:
                    path.rename(root / 'retired' / path.name)
        print(json.dumps({'deleted_files': len(selected), 'deferred_files': len(deferred),
                          'allocated_bytes_reclaimed': allocated,
                          'deletion_log': str(log_path), 'retired': args.retire}))
    else:
        files, allocated = [], 0
        for target in paths:
            for path in waveform_files(target):
                if str(path.relative_to(REPO)) in tracked:
                    raise ValueError('selected run contains tracked waveform')
                allocated += path.stat().st_blocks * 512
                files.append({'path': str(path.relative_to(root)), 'fingerprint': fingerprint(path)})
        plan = {'root': str(root), 'created_at_epoch': time.time(), 'targets': targets,
                'files': files, 'allocated_bytes': allocated,
                'retained': 'All non-waveform files, including workloads, ledgers, measurements and netlists.'}
        args.plan.parent.mkdir(parents=True, exist_ok=True)
        with args.plan.open('x') as output:
            output.write(json.dumps(plan, indent=2) + '\n')
        print(json.dumps({'planned_files': len(files), 'allocated_bytes': allocated,
                          'targets': targets, 'plan': str(args.plan)}))


if __name__ == '__main__':
    main()
