import pytest

from agcws.policies.semantic_edits import apply_edits


def test_edits_preserve_parent_and_materialize_workload():
    parents = [{'operations': [{'op': 'encrypt', 'blocks': 50}]}]
    child = apply_edits(parents, {'parent': 0, 'edits': [
        {'path': ['operations', 0, 'blocks'], 'value': 75}]})
    assert child['operations'][0]['blocks'] == 75
    assert parents[0]['operations'][0]['blocks'] == 50


@pytest.mark.parametrize('path', [[], ['missing'], ['operations', -1, 'blocks'],
                                 ['operations', True, 'blocks'], ['operations']])
def test_edits_reject_invalid_paths_and_container_replacement(path):
    with pytest.raises(ValueError):
        apply_edits([{'operations': [{'blocks': 50}]}],
                    {'parent': 0, 'edits': [{'path': path, 'value': 75}]})
