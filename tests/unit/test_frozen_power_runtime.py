import json

import pytest

from agcws.core.provenance import file_sha256
from agcws.evaluation.power.frozen import verify_sources


def test_original_paths_are_verified_not_remapped(tmp_path):
    source = tmp_path / "original.py"
    source.write_text("original")
    manifest = {"sources": {"original.py": file_sha256(source)}}
    assert verify_sources(manifest, tmp_path) == tmp_path
    source.write_text("refactored")
    with pytest.raises(ValueError, match="differs"):
        verify_sources(manifest, tmp_path)


@pytest.mark.parametrize("path", ["../outside.py", "/absolute.py"])
def test_unsafe_source_reference_rejected(tmp_path, path):
    with pytest.raises(ValueError, match="unsafe"):
        verify_sources({"sources": {path: "digest"}}, tmp_path)


def test_empty_inventory_is_not_provenance(tmp_path):
    with pytest.raises(ValueError, match="nonempty"):
        verify_sources({"sources": {}}, tmp_path)


@pytest.mark.parametrize('registry', ['pipeline/backends.py', 'designs/temporal_registry.py'])
def test_redmule_replay_preserves_verified_host_dependency_path(tmp_path, monkeypatch, registry):
    from agcws.evaluation.power import frozen

    runtime, deps, scratch = tmp_path / 'runtime', tmp_path / 'deps', tmp_path / 'scratch'
    entry = runtime / 'src/agcws' / registry
    entry.parent.mkdir(parents=True)
    entry.write_text('original')
    deps.mkdir()
    (deps / 'rtl.sv').write_text('RTL')
    monkeypatch.setattr(frozen.config, 'path_setting', lambda *_: deps)
    manifest = {'spec': {'domain': 'redmule-temporal-long'}, 'runtime': {},
                'sources': {str(entry.relative_to(runtime)): file_sha256(entry),
                            '.dependencies/rtl.sv': file_sha256(deps / 'rtl.sv')}}

    def subprocess_run(command, *, cwd, env, **kwargs):
        assert cwd == runtime
        assert registry.removesuffix('.py').replace('/', '.') in command[2]
        assert env['AGCWS_REDMULE_DEPS'] == str(deps)
        (scratch / 'replay-result.json').write_text(json.dumps({'valid': True, 'rates': [1] * 8}))

    monkeypatch.setattr(frozen.subprocess, 'run', subprocess_run)
    result = frozen.replay({'rates': [1] * 8}, manifest, runtime, scratch)
    assert result['valid']
    assert (scratch / 'replay-receipt.json').exists()


def test_dependency_hash_and_domain_are_required(tmp_path, monkeypatch):
    from agcws.evaluation.power import frozen

    deps = tmp_path / 'deps'
    deps.mkdir()
    source = deps / 'rtl.sv'
    source.write_text('rtl')
    monkeypatch.setattr(frozen.config, 'path_setting', lambda *_: deps)
    manifest = {'spec': {'domain': 'redmule-temporal-long'},
                'sources': {'.dependencies/rtl.sv': file_sha256(source)}}
    verify_sources(manifest, tmp_path)
    source.write_text('changed')
    with pytest.raises(ValueError, match='differs'):
        verify_sources(manifest, tmp_path)
    manifest['spec']['domain'] = 'aes-temporal'
    with pytest.raises(ValueError, match='unexpected external'):
        verify_sources(manifest, tmp_path)


def test_ibex_replay_copies_verified_simulator(tmp_path, monkeypatch):
    from agcws.evaluation.power import frozen

    runtime = tmp_path / 'runtime'
    entry = runtime / 'src/agcws/designs/temporal_registry.py'
    entry.parent.mkdir(parents=True)
    entry.write_text('registry')
    study, scratch = tmp_path / 'study', tmp_path / 'scratch'
    relative = 'toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system'
    binary = study / relative
    binary.parent.mkdir(parents=True)
    binary.write_text('simulator')
    binary.chmod(0o755)
    manifest = {'spec': {'domain': 'ibex-temporal'},
                'runtime': {'binary_sha256': file_sha256(binary)},
                'sources': {str(entry.relative_to(runtime)): file_sha256(entry)}}

    def execute(*args, **kwargs):
        assert file_sha256(scratch / relative) == file_sha256(binary)
        assert (scratch / relative).stat().st_mode & 0o111
        (scratch / 'replay-result.json').write_text(json.dumps(
            {'valid': True, 'profile': {'window_rates': [1] * 8}}))

    monkeypatch.setattr(frozen.subprocess, 'run', execute)
    case = {'root': str(study), 'rates': [1] * 8}
    assert frozen.replay(case, manifest, runtime, scratch)['rates'] == [1] * 8
    binary.write_text('different simulator')
    with pytest.raises(ValueError, match='binary differs'):
        frozen.replay(case, manifest, runtime, tmp_path / 'second')
