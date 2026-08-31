from pathlib import Path


def test_aes_pdk_corpus_runner_is_fail_closed():
    text = Path("scripts/run_aes_pdk_corpus.sh").read_text()
    assert "at least two trial workloads" in text
    assert "missing waveform" in text
    assert "validate_aes_pdk_corpus.py" in text
    assert "write_aes_pdk_manifest.py" in text
    assert "run-manifest.json" in text
