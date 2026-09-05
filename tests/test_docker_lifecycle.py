import json
import os
import subprocess
from pathlib import Path


def test_run_wrapper_uses_disposable_nonroot_container(tmp_path):
    fake = tmp_path / 'docker'
    fake.write_text('#!/usr/bin/env python3\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\n')
    fake.chmod(0o755)
    environment = {**os.environ, 'PATH': f'{tmp_path}:{os.environ["PATH"]}',
                   'AGCWS_CONTAINER_OUTPUT': str(tmp_path / 'artifacts'),
                   'AGCWS_CONTAINER_IMAGE': 'test-image'}
    root = Path(__file__).parents[1]
    result = subprocess.run(['bash', str(root / 'docker/run.sh'), 'echo', 'two words'],
                            env=environment, capture_output=True, text=True, check=True)
    args = json.loads(result.stdout)
    assert args[:4] == ['run', '--rm', '--init', '--read-only']
    assert args[args.index('--user') + 1] == f'{os.getuid()}:{os.getgid()}'
    assert args[args.index('--cap-drop') + 1] == 'ALL'
    assert 'io.agcws.project=agcws' in args
    assert f'io.agcws.owner={os.getuid()}' in args
    assert any('dst=/workspace,readonly' in arg for arg in args)
    assert any('dst=/workspace/out' in arg for arg in args)
    assert args[-3:] == ['test-image', 'echo', 'two words']


def test_prune_preview_does_not_delete(tmp_path):
    calls = tmp_path / 'calls.jsonl'
    fake = tmp_path / 'docker'
    fake.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                    'with open(os.environ["TEST_DOCKER_CALLS"], "a") as f:\n'
                    ' f.write(json.dumps(sys.argv[1:]) + "\\n")\n')
    fake.chmod(0o755)
    environment = {**os.environ, 'PATH': f'{tmp_path}:{os.environ["PATH"]}',
                   'TEST_DOCKER_CALLS': str(calls)}
    script = Path(__file__).parents[1] / 'docker/prune.sh'
    subprocess.run(['bash', str(script)], env=environment, check=True, capture_output=True)
    requests = [json.loads(line) for line in calls.read_text().splitlines()]
    assert len(requests) == 2
    assert all('prune' not in request for request in requests)
    assert all('label=io.agcws.project=agcws' in request for request in requests)
    subprocess.run(['bash', str(script), '--apply'], env=environment, check=True, capture_output=True)
    requests = [json.loads(line) for line in calls.read_text().splitlines()]
    prunes = [r for r in requests if 'prune' in r]
    assert len(prunes) == 3
    assert all('system' not in r and 'volume' not in r for r in requests)
    assert all(f'label=io.agcws.owner={os.getuid()}' in r for r in prunes[:2])
    assert prunes[2][prunes[2].index('--builder') + 1] == f'agcws-{os.getuid()}'
