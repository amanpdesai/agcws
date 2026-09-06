from pathlib import Path

from analysis.freeze_structural import snapshot


def test_cross_design_snapshot_uses_same_controller_without_provider_call(monkeypatch):
    monkeypatch.setenv('AGCWS_GEMINI_MODEL', 'test-model')
    templates = [snapshot(d, 'population-hybrid', 'random_300', 400, 32,
                          Path(f'results/structural_temporal_{d}_verification.json'))
                 for d in ('aes', 'dma')]
    for key in ('policy', 'model', 'prompt_hash', 'sampling', 'source_digest'):
        assert templates[0][key] == templates[1][key]
    assert templates[0]['model'] == 'test-model'
    assert templates[0]['goal']['observation_cycles'] == 6774
    assert templates[1]['goal']['observation_cycles'] == 12000
    assert all(t['seed'] == 400 and t['budget'] == 32 for t in templates)
