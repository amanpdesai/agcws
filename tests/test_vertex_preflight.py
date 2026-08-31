from pathlib import Path

from scripts.vertex_preflight import preflight


def test_vertex_preflight_reports_missing_nonsecret_config(tmp_path: Path):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("frozen prompt\n")
    result = preflight(prompt, None, None)
    assert not result["valid"]
    assert result["missing"] == ["AGCWS_GCP_PROJECT", "AGCWS_GEMINI_MODEL"]
    assert result["prompt_sha256"]
