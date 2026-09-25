import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from agcws.designs.aes.gls import sha
from agcws.evaluation.simulation import cached_verilator as cache


def setup(tmp_path, monkeypatch):
    prepared = tmp_path / 'prepared'
    prepared.mkdir()
    source = prepared / 'mapped.v'
    source.write_text('module test; endmodule')
    replay = prepared / 'replay.vlt'
    replay.write_text(str(source))
    (prepared / 'preparation.json').write_text(json.dumps({
        'sources': {str(source): sha(source)}, 'generated': {'replay.vlt': sha(replay)}}))
    compiler = tmp_path / 'verilator'
    compiler.write_text('compiler')
    calls = []

    def compile(command, **kwargs):
        calls.append(command)
        Path(command[command.index('-o') + 1]).write_text('compiled simulator')

    monkeypatch.setattr(cache.subprocess, 'run', compile)

    def args(label):
        dest = tmp_path / label
        dest.mkdir()
        waiver = dest / 'waiver.vlt'
        waiver.write_text('same waiver')
        return ['--binary', '-f', str(replay), str(source), str(waiver),
                '--Mdir', str(dest / 'obj'), '-o', str(dest / 'obj/simulate'), '-j', '8']

    return str(compiler), args, calls, source


def test_workload_paths_share_build_and_lock(tmp_path, monkeypatch):
    compiler, args, calls, _ = setup(tmp_path, monkeypatch)
    commands = [args(str(i)) for i in range(4)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda a: cache.cached_compile(
            a, compiler, tmp_path / 'cache', 'image-id'), commands))
    assert len(calls) == 1
    assert calls[0][calls[0].index('-j') + 1] == '2'
    assert len({r['key'] for r in results}) == 1
    assert sum(r['hit'] for r in results) == 3


def test_cache_integrity_failure_is_not_silently_rebuilt(tmp_path, monkeypatch):
    compiler, args, calls, _ = setup(tmp_path, monkeypatch)
    result = cache.cached_compile(args('a'), compiler, tmp_path / 'cache', 'image')
    (tmp_path / 'cache' / result['key'] / 'simulate').write_text('tampered')
    with pytest.raises(ValueError, match='integrity'):
        cache.cached_compile(args('b'), compiler, tmp_path / 'cache', 'image')
    assert len(calls) == 1


def test_changed_source_is_rejected_and_image_changes_key(tmp_path, monkeypatch):
    compiler, args, calls, source = setup(tmp_path, monkeypatch)
    a = cache.cached_compile(args('a'), compiler, tmp_path / 'cache', 'image1')
    b = cache.cached_compile(args('b'), compiler, tmp_path / 'cache', 'image2')
    assert a['key'] != b['key'] and len(calls) == 2
    source.write_text('changed')
    with pytest.raises(ValueError, match='source changed'):
        cache.cached_compile(args('c'), compiler, tmp_path / 'cache', 'image2')


def test_failed_compilation_does_not_publish_cache(tmp_path, monkeypatch):
    compiler, args, _, _ = setup(tmp_path, monkeypatch)

    def fail(*args, **kwargs):
        raise RuntimeError('compile failed')

    monkeypatch.setattr(cache.subprocess, 'run', fail)
    with pytest.raises(RuntimeError, match='compile failed'):
        cache.cached_compile(args('a'), compiler, tmp_path / 'cache', 'image')
    assert not list((tmp_path / 'cache').glob('*/receipt.json'))
