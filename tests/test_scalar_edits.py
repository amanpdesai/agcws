import copy
from types import SimpleNamespace

from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.policies.random_search import RandomSearch
from agcws.policies.scalar_edits import ScalarEditEvolution, editable_fields


def test_scalar_edits_share_random_initialization():
    adapter = AESTransactionAdapter()
    assert ScalarEditEvolution(17).propose(adapter, None, [], 4) == RandomSearch(17).propose(adapter, None, [], 4)


def test_scalar_edits_preserve_parent_and_structure():
    adapter = AESTransactionAdapter()
    parent = RandomSearch(17).propose(adapter, None, [], 1)[0]
    original = copy.deepcopy(parent)
    trial = SimpleNamespace(workload=parent, loss=0.1, validity=SimpleNamespace(valid=True))
    children = ScalarEditEvolution(9).propose(adapter, None, [trial], 30)
    assert parent == original
    assert len(children) == 30
    assert all(len(child['operations']) == len(parent['operations']) for child in children)
    assert any(child != parent for child in children)


def test_editable_fields_exclude_constants_and_containers():
    schema = {'type': 'object', 'properties': {
        'op': {'const': 'idle'}, 'cycles': {'type': 'integer', 'minimum': 1, 'maximum': 10}}}
    assert editable_fields({'op': 'idle', 'cycles': 5}, schema) == [(('cycles',), 5, schema['properties']['cycles'])]


def test_no_editable_fields_still_consumes_candidate_slot():
    adapter = SimpleNamespace(workload_schema={'type': 'object', 'properties': {'op': {'const': 'fixed'}}})
    trial = SimpleNamespace(workload={'op': 'fixed'}, loss=1, validity=SimpleNamespace(valid=True))
    assert ScalarEditEvolution().propose(adapter, None, [trial], 2) == [{'op': 'fixed'}, {'op': 'fixed'}]
