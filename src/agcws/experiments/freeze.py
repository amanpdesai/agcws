"""Reject runtime drift before a frozen run proposes its first candidate."""


def verify_frozen_manifest(actual, template, seed, profile):
    expected = {**template, 'seed': seed, 'goal': {**template['goal'], 'profile': profile}}
    for key, value in expected.items():
        if key != 'source_commit' and actual.get(key) != value:
            raise ValueError(f'frozen manifest mismatch: {key}')
