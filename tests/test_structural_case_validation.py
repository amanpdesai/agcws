import json
from types import SimpleNamespace

import pytest

from validation.structural_case import run_case


def test_undeclared_case_fails_before_tools(tmp_path, monkeypatch):
    frozen = tmp_path / 'freeze.json'
    frozen.write_text(json.dumps({'spec': {'designs': ['aes', 'dma'],
                                         'targets': ['random_300', 'random_301'],
                                         'policies': ['random'], 'seeds': list(range(400, 410))}}))

    def no_tool(*args, **kwargs):
        raise AssertionError('no tool should run')

    monkeypatch.setattr('validation.structural_case.subprocess.run', no_tool)
    with pytest.raises(ValueError, match='not a declared'):
        run_case(SimpleNamespace(freeze=frozen, design='aes', target='invented', policy='random'))
