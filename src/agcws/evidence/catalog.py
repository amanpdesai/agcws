"""Locate final results without rewriting paths inside frozen records."""

import json
from pathlib import Path, PurePosixPath


def load(root):
    data = json.loads((Path(root) / 'results/index.json').read_text())
    if data['version'] != 2:
        raise ValueError('unsupported results index')
    return data


def safe_path(root, name):
    relative = PurePosixPath(name)
    if not relative.parts or relative.is_absolute() or '..' in relative.parts or str(relative) != name:
        raise ValueError(f'unsafe catalog path: {name}')
    root = Path(root).resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError('catalog path escapes repository')
    return path


def summary(root, name):
    return safe_path(root, load(root)['summaries'][name])


def design(root, name, kind):
    return safe_path(root, load(root)['designs'][name][kind])


def resolve(root, recorded):
    """Resolve an original evidence identity or a current repository path."""
    safe_path(root, recorded)
    aliases = load(root)['relocations']
    for old in sorted(aliases, key=len, reverse=True):
        if recorded == old or recorded.startswith(old + '/'):
            return safe_path(root, aliases[old] + recorded[len(old):])
    return safe_path(root, recorded)


def recorded(root, current):
    """Keep established source labels in regenerated summaries."""
    relative = str(Path(current).relative_to(root))
    aliases = load(root)['relocations']
    for old, new in sorted(aliases.items(), key=lambda item: len(item[1]), reverse=True):
        if relative == new or relative.startswith(new + '/'):
            return old + relative[len(new):]
    return relative
