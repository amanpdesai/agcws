from pathlib import Path


def test_container_uses_image_python_when_workspace_is_mounted():
    text = Path("docker/Dockerfile").read_text()
    assert "VENV_PYTHON=python" in text
    assert "MPLCONFIGDIR=/tmp/matplotlib" in text


def test_container_includes_pinned_memory_generator():
    text = Path("docker/Dockerfile").read_text()
    assert "COPY benchmarks/support/bsg_fakeram /opt/agcws/benchmarks/support/bsg_fakeram" in text
