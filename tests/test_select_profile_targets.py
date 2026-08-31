import json
from pathlib import Path

from scripts.select_profile_targets import select


def test_profile_selection_is_deterministic_and_normalizes_regions(tmp_path: Path):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("\n".join([
        json.dumps({"index": 0, "by_region": {"a": 2, "b": 2}}),
        json.dumps({"index": 1, "by_region": {"a": 1, "b": 3}}),
        json.dumps({"index": 2, "by_region": {"a": 3, "b": 1}}),
    ]) + "\n")
    first = select(corpus, "compositional", seed=7)
    second = select(corpus, "compositional", seed=7)
    assert first == second
    assert sum(first[0]["shares"].values()) == 1.0


def test_temporal_selection_preserves_achieved_waveform(tmp_path: Path):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text(json.dumps({"name": "burst", "normalized_windows": [1.0, 0.5]}) + "\n")
    assert select(corpus, "temporal")[0]["profile"] == [1.0, 0.5]
