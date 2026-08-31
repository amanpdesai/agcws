from pathlib import Path


def test_container_uses_image_python_when_workspace_is_mounted():
    text = Path("docker/Dockerfile").read_text()
    assert "VENV_PYTHON=python" in text
    assert "MPLCONFIGDIR=/tmp/matplotlib" in text
