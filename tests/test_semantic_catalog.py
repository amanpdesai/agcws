import pytest

from agcws.policies.semantic_catalog import materialize_catalog_patch


def test_catalog_materializes_without_mutating_parent():
    parents = [{'cycles': 3}]
    catalog = {'p0f0': {'parent': 0, 'path': ['cycles']}}
    assert materialize_catalog_patch(parents, catalog, {'edits': [{'field': 'p0f0', 'value': 8}]}) == {'cycles': 8}
    assert parents == [{'cycles': 3}]


def test_catalog_rejects_mixed_parents():
    catalog = {f'p{i}f0': {'parent': i, 'path': ['cycles']} for i in range(2)}
    with pytest.raises(ValueError, match='one parent'):
        materialize_catalog_patch([{'cycles': 3}] * 2, catalog,
                                  {'edits': [{'field': 'p0f0', 'value': 4}, {'field': 'p1f0', 'value': 4}]})


def test_catalog_does_not_repair_unknown_ids():
    with pytest.raises(KeyError):
        materialize_catalog_patch([], {}, {'edits': [{'field': 'invented', 'value': 1}]})
