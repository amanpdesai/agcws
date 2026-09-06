import copy

import pytest

from analysis.audit_structural_heldout import verify_frozen_manifest


def template():
    return {'source_commit': 'before', 'source_digest': 'fixed', 'seed': 400,
            'goal': {'profile': [1, 2], 'scale': 40}, 'model': 'frozen-model',
            'budget': 32, 'prompt_hash': 'prompt', 'sampling': {'temperature': 0.7}}


def test_only_cell_identity_and_nonexecutable_commit_may_change():
    expected = template()
    actual = {**expected, 'source_commit': 'docs-only-commit', 'seed': 402,
              'goal': {'profile': [2, 1], 'scale': 40}}
    verify_frozen_manifest(actual, expected, 402, [2, 1])


@pytest.mark.parametrize('field', ['source_digest', 'model', 'budget', 'prompt_hash', 'sampling'])
def test_frozen_runtime_changes_fail(field):
    expected = template()
    actual = copy.deepcopy(expected)
    actual[field] = 'changed'
    with pytest.raises(ValueError, match='frozen manifest mismatch'):
        verify_frozen_manifest(actual, expected, 400, [1, 2])
