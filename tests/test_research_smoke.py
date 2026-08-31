from pathlib import Path


def test_research_smoke_exercises_profile_goal_paths():
    text = Path("scripts/research_smoke.sh").read_text()
    assert "run_aes_temporal_search.py" in text
    assert "run_aes_compositional_search.py" in text
    assert "AGCWS_PROFILE_SMOKE_BUDGET" in text
    assert '"normalized_windows"' in text
    assert '"waveform_sha256"' in text
