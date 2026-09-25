import pytest

from agcws.studies import finalists


def test_verified_inputs_are_hashed_once_until_metadata_changes(tmp_path, monkeypatch):
    source = tmp_path / 'trials.json'
    source.write_text('original')
    body = {'inputs': {str(source): finalists.sha(source)}, 'cases': [], 'omitted': []}
    plan = {**body, 'sha256': finalists.key(body)}
    original = finalists.sha
    calls = []

    def digest(path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(finalists, 'sha', digest)
    finalists.verify(plan)
    finalists.verify(plan)
    assert len(calls) == 1
    source.write_text('modified')
    with pytest.raises(ValueError, match='input changed'):
        finalists.verify(plan)
    assert len(calls) == 2


def test_mutation_during_hashing_is_rejected(tmp_path, monkeypatch):
    source = tmp_path / 'input'
    source.write_text('before')
    body = {'inputs': {str(source): finalists.sha(source)}, 'cases': [], 'omitted': []}
    plan = {**body, 'sha256': finalists.key(body)}

    def digest(path):
        path.write_text('after')
        return body['inputs'][str(path)]

    monkeypatch.setattr(finalists, 'sha', digest)
    with pytest.raises(ValueError, match='while hashing'):
        finalists.verify(plan)
