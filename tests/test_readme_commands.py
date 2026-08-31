from pathlib import Path


def test_readme_uses_makefile_artifact_root_variable():
    text = Path("README.md").read_text()
    assert "AGCWS_ARTIFACT_ROOT=out/aes-pdk-validation" in text
    assert "  ARTIFACT_ROOT=out/aes-pdk-validation" not in text
