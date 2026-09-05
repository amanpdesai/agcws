"""Record the selected controller and executable configuration before evaluation."""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.adapters.axi_dma.pipelined import PipelinedDmaAdapter
from agcws.experiments.provenance import capture_run
from agcws.goals.schema import ScalarGoal
from agcws.policies.semantic_catalog import SemanticCatalog
from agcws.policies.semantic_edits import SemanticEditsBounded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    selection = json.loads(args.selection.read_text())
    model = os.environ.get('AGCWS_GEMINI_MODEL')
    if model != selection['model']:
        raise ValueError('environment model differs from selected development model')
    policy_class, prompt_path = {
        'semantic-edits-v4': (SemanticEditsBounded, 'prompts/semantic_edits_v3.txt'),
        'semantic-catalog-v5': (SemanticCatalog, 'prompts/semantic_catalog_v5.txt'),
    }[selection['selected_policy']]
    prompt = Path(prompt_path).read_text()
    policy = policy_class(lambda *args: '', prompt, model=model)
    profiles = {}
    for design, adapter, calibration_path in [
        ('aes', AESTransactionAdapter(), 'results/aes_transactions_calibration/calibration.json'),
        ('dma', PipelinedDmaAdapter(), 'results/dma_pipelined_calibration/calibration.json'),
    ]:
        calibration = json.loads(Path(calibration_path).read_text())
        matching = [s['manifest'] for s in selection['sources']
                    if s['manifest']['design'] == design
                    and policy.name in s['manifest']['policies']]
        if len(matching) != 1 or matching[0]['calibration'] != calibration:
            raise ValueError('calibration differs from selected development panel')
        if matching[0]['prompt_sha256'] != hashlib.sha256(prompt.encode()).hexdigest():
            raise ValueError('prompt differs from selected development panel')
        profiles[design] = capture_run(adapter, policy, ScalarGoal(0.5, 0.02),
                                       50, 4, 200, calibration['p_min'], calibration['p_max'])
    record = {'frozen_at': datetime.now(timezone.utc).isoformat(),
              'selected_policy': policy.name, 'model': model, 'prompt_path': prompt_path,
              'selection_sha256': hashlib.sha256(args.selection.read_bytes()).hexdigest(),
              'targets': [0.1, 0.25, 0.5, 0.75, 0.9], 'seeds': list(range(200, 210)),
              'configuration_templates': profiles,
              'scope': 'Pre-run snapshot; template goal/seed is replaced by each declared cell.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as output:
        output.write(json.dumps(record, indent=2) + '\n')
    print(f'frozen {policy.name}; no proposals or API calls executed')


if __name__ == '__main__':
    main()
