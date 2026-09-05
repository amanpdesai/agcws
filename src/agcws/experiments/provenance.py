"""Capture executable experiment configuration before any proposals are made."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version


def capture_run(adapter, policy, goal, budget, batch_size, seed, p_min, p_max):
    root = Path(__file__).resolve().parents[3]
    sources = [*root.joinpath('src/agcws').rglob('*.py'),
               *root.joinpath('scripts').glob('*.py'),
               *root.joinpath('scripts').glob('*.sh'),
               *root.joinpath('experiments').glob('*.sv'),
               *root.joinpath('experiments').glob('*.svh'),
               *root.joinpath('third_party/harnesses').glob('*.py')]
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(sources)}
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    packages = {}
    for name in ['google-genai', 'jsonschema', 'cocotb', 'cocotbext-axi', 'cryptography']:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    return {'source_commit': commit, 'source_hashes': hashes,
            'python': sys.version, 'packages': packages,
            'source_digest': hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
            'adapter': type(adapter).__name__, 'policy': policy.name,
            'schema_sha256': hashlib.sha256(json.dumps(adapter.workload_schema, sort_keys=True).encode()).hexdigest(),
            'goal': vars(goal), 'budget': budget, 'batch_size': batch_size, 'seed': seed,
            'p_min': p_min, 'p_max': p_max, 'useful_work_floor': adapter.useful_work_floor,
            'model': getattr(policy, 'model', None), 'prompt_hash': getattr(policy, 'prompt_hash', None),
            'sampling': {key: getattr(policy, key, None) for key in
                         ['temperature', 'top_p', 'max_output_tokens', 'thinking_budget', 'proposal_attempts']},
            'pricing': {key: os.getenv('AGCWS_GEMINI_' + key) for key in
                        ['INPUT_USD_PER_MILLION', 'OUTPUT_USD_PER_MILLION']}}
