from pathlib import Path


def test_scalar_search_cli_exposes_declared_policies():
    text = Path("scripts/run_aes_search.py").read_text()
    for policy in ("random", "mutation", "evolutionary", "offline-agent", "offline-hybrid", "vertex"):
        assert policy in text
    assert "AGCWS_GEMINI_MODEL" in text
    assert "AGCWS_GCP_PROJECT" in text
    assert 'choices=("activity", "synthesis")' in text
    assert 'default="activity"' in text


def test_scalar_search_cli_uses_preregistered_primary_tolerance():
    text = Path("scripts/run_aes_search.py").read_text()
    assert 'parser.add_argument("--epsilon", type=float, default=0.05)' in text
