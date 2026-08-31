from pathlib import Path


def test_scalar_search_cli_exposes_declared_policies():
    text = Path("scripts/run_aes_search.py").read_text()
    for policy in ("random", "mutation", "evolutionary", "offline-agent"):
        assert policy in text
