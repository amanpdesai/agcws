import pytest
import json
from types import SimpleNamespace

from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.adapters.axi_dma.pipelined import PipelinedDmaAdapter
from agcws.adapters.base import Validity
from agcws.goals.schema import ScalarGoal
from agcws.nodes.validation import validate_static
from agcws.policies.semantic_catalog import SemanticCatalog, materialize_catalog_patch


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


@pytest.mark.parametrize('adapter', [AESTransactionAdapter(), PipelinedDmaAdapter()])
def test_catalog_proposal_roundtrip_uses_same_controller_for_both_designs(adapter):
    calls = []

    def generate(model, text):
        payload = json.loads(text)
        calls.append(payload)
        key, entry = next(iter(payload['editable_fields'].items()))
        return json.dumps([{'edits': [{'field': key, 'value': entry['current']}]}]), {'tokens_in': 10, 'tokens_out': 5}

    policy = SemanticCatalog(generate, 'test', model='test').initialize(100, 1, 100)
    goal = ScalarGoal(0.5, 0.02)
    initial = policy.propose(adapter, goal, [], 4)
    assert calls == []
    history = [SimpleNamespace(workload=w, validity=Validity(True), loss=0.1,
                               profile=SimpleNamespace(mean_power=50, useful_work=10000)) for w in initial]
    proposed = policy.propose(adapter, goal, history, 1)
    assert len(calls) == 1
    assert proposed == [initial[0]]
    assert validate_static(adapter, proposed[0]).valid
    assert policy.last_usage == {'tokens_in': 10, 'tokens_out': 5}
