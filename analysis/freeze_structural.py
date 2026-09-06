"""Freeze the selected temporal family only after a complete development audit."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from agcws import config
from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.adapters.axi_dma.temporal import DmaTemporalAdapter
from agcws.experiments.provenance import capture_run
from agcws.goals.schema import FixedTemporalGoal
from agcws.policies.structural import (
    StructuralEvolution,
    StructuralPopulationEvolution,
    StructuralRandom,
)
from agcws.policies.structural_edit_agent import (
    StructuralEditAgent,
    StructuralEditHybrid,
    StructuralPopulationAgent,
    StructuralPopulationHybrid,
)
from agcws.workloads.schedule import ScheduleContract
from analysis.audit_structural_panel import build, require

CLASSES = {'random': StructuralRandom, 'evolutionary': StructuralEvolution,
           'population-evolution': StructuralPopulationEvolution,
           'edit-agent': StructuralEditAgent, 'edit-hybrid': StructuralEditHybrid,
           'population-agent': StructuralPopulationAgent, 'population-hybrid': StructuralPopulationHybrid}


def snapshot(design, policy_name, target_name, seed, budget, corpus_path):
    config._load_dotenv()
    corpus = json.loads(corpus_path.read_text())
    reference = next(row for row in corpus['cases'] if row['name'] == target_name)
    adapter = {'aes': AESTemporalAdapter, 'dma': DmaTemporalAdapter}[design](ScheduleContract(**corpus['contract']))
    goal = FixedTemporalGoal(windows=8, profile=reference['window_rates'],
                             scale={'aes': 200.0, 'dma': 40.0}[design],
                             observation_cycles=reference['clock_edges'], tolerance=0.1)
    cls = CLASSES[policy_name]
    if policy_name.endswith(('agent', 'hybrid')):
        prompt = Path('prompts/structural_temporal_edits_v2.txt').read_text()
        policy = cls(lambda *_: '', prompt, model=os.environ['AGCWS_GEMINI_MODEL']).initialize(seed)
    else:
        policy = cls(seed)
    return capture_run(adapter, policy, goal, budget, 4, seed, None, None)


def freeze(development):
    report = build(development)
    family = report['selected_family']
    policies = (['random', 'evolutionary', 'edit-agent', 'edit-hybrid'] if family == 'best-eight'
                else ['random', 'population-evolution', 'population-agent', 'population-hybrid'])
    spec = {'phase': 'held-out', 'selected_family': family, 'designs': ['aes', 'dma'],
            'targets': ['random_300', 'random_301'], 'seeds': list(range(400, 410)),
            'budget': 32, 'batch_size': 4, 'policies': policies}
    templates, corpora = {}, {}
    for design in spec['designs']:
        path = Path(f'results/structural_temporal_{design}_verification.json')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        archived = json.loads((development / design / 'random_300' / 'seed-315' / 'random'
                               / 'target_manifest.json').read_text())
        require(digest == archived['source_sha256'], 'reference corpus changed since development')
        corpora[design] = {'path': str(path), 'sha256': digest}
        for policy in policies:
            template = snapshot(design, policy, 'random_300', 400, 32, path)
            if template['model']:
                require({k: template[k] for k in report['agent_configuration']}
                        == report['agent_configuration'], 'selected controller configuration changed')
            templates[f'{design}/{policy}'] = template
    transport = {k: os.getenv(k, default) for k, default in {
        'AGCWS_GCP_PROJECT': '', 'AGCWS_GCP_LOCATION': 'global', 'AGCWS_VERTEX_TIMEOUT_S': '60',
    }.items()}
    return {'spec': spec, 'development_family_scores': report['family_scores'],
            'development_source_digest': report['source_digest'],
            'development_artifact_sha256': report['artifact_sha256'],
            'templates': templates, 'corpora': corpora, 'transport': transport,
            'claim_scope': 'Fresh search seeds on observed activity-profile tasks; no unseen-target or power claim.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--development', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args.development)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(result['spec']['selected_family'])


if __name__ == '__main__':
    main()
