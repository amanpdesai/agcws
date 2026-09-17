import copy
import gzip
import hashlib
import json

import pytest

from analysis.audit_model_visibility import check_goal, check_history, load_bundle


def fixture():
    history = [dict(slot=1, rates=[1.0]*8, valid=True, program={'x': 1}, prediction=None),
               dict(slot=2, rates=[2.0]*8, valid=True, program={'x': 2},
                    prediction={'reference_slot': 1, 'window_directions': [1]*8})]
    payload = {'goal': {'scale': 10}, 'history': copy.deepcopy(history),
               'experiment_notebook': [{'slot': 2, 'prediction': history[1]['prediction'],
                                       'scorable': True, 'normalized_delta': [.1]*8,
                                       'observed_directions': [1]*8}]}
    return payload, history


def test_valid_prior_history():
    check_history(*fixture())


@pytest.mark.parametrize('mutation', ['future', 'other_program', 'other_rate', 'notebook_delta'])
def test_injected_history_fails(mutation):
    payload, history = fixture()
    if mutation == 'future':
        payload['history'][0]['slot'] = 99
    elif mutation == 'other_program':
        payload['history'][0]['program'] = {'hidden_witness': True}
    elif mutation == 'other_rate':
        payload['history'][0]['rates'][0] = 12
    else:
        payload['experiment_notebook'][0]['normalized_delta'][0] = 12
    with pytest.raises(ValueError):
        check_history(payload, history)


def test_injected_goal_fields_rejected():
    with pytest.raises(ValueError, match='unexpected goal'):
        check_goal({'witness': 'answer'}, {}, 't')


def test_archive_tampering_rejected(tmp_path):
    path = tmp_path/'bundle.gz'
    bundle = {'a.json': {'text': '{}', 'sha256': hashlib.sha256(b'{}').hexdigest()}}
    path.write_bytes(gzip.compress(json.dumps(bundle).encode()))
    assert load_bundle(path) == {'a.json': {}}
    bundle['a.json']['text'] = '{"answer": 1}'
    path.write_bytes(gzip.compress(json.dumps(bundle).encode()))
    with pytest.raises(ValueError, match='checksum'):
        load_bundle(path)
