from pathlib import Path

import pytest

from agcws.designs.redmule import container


def test_container_boundary_rejects_paths_outside_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(container.config, 'ROOT', tmp_path)
    assert container.container_path(tmp_path / 'out/run') == Path('/workspace/out/run')
    with pytest.raises(ValueError):
        container.container_path(tmp_path.parent / 'elsewhere')


def test_container_recipe_resolves_image_before_launch(tmp_path, monkeypatch):
    deps = tmp_path / 'deps'
    deps.mkdir()
    monkeypatch.setattr(container.config, 'ROOT', tmp_path)
    monkeypatch.setattr(container.config, 'path_setting', lambda *_: deps)
    monkeypatch.setattr(container.subprocess, 'check_output', lambda *a, **kw: 'sha256:pinned\n')
    calls = []
    monkeypatch.setattr(container.subprocess, 'run', lambda *a, **kw: calls.append((a, kw)))
    assert container.invoke('print("diagnostic")', []) == 'sha256:pinned'
    command, options = calls[0][0][0], calls[0][1]
    assert command[:2] == ['bash', str(tmp_path / 'docker/run.sh')]
    assert options['env']['AGCWS_CONTAINER_IMAGE'] == 'sha256:pinned'
    assert options['env']['AGCWS_CONTAINER_DEPS'] == str(deps)
    assert options['check'] is True


def test_reference_clock_preserves_native_artifacts(tmp_path):
    native = '$timescale 1ps $end\n$enddefinitions $end\n#0\n0!\n#1000\n1!\n'
    for name in ('gls.vcd', 'rtl.vcd'):
        (tmp_path / name).write_text(native)
    result = {'waveform': str(tmp_path / 'gls.vcd'), 'rtl_waveform': str(tmp_path / 'rtl.vcd'),
              'bounds': None, 'expected_period_s': 1e-9}
    converted = container.reference_clock(result, tmp_path)
    assert converted['expected_period_s'] == 1e-8
    assert (tmp_path / 'gls.vcd').read_text() == native
    assert Path(converted['waveform']).read_text() == native.replace('#1000', '#10000')
    assert result['expected_period_s'] == 1e-9
