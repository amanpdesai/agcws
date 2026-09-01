from pathlib import Path


def test_container_smoke_checks_frontend_and_both_liberties():
    text = Path("scripts/container_smoke.sh").read_text()
    assert "help read_slang" in text
    assert "AGCWS_LIBERTY_NANGATE45" in text
    assert "run_axi_dma_workload.py" in text
    assert "axi_dma_smoke.json" in text
    assert "artifact_root=${AGCWS_ARTIFACT_ROOT:-out}" in text
    assert '"$artifact_root/container-ibex-smoke"' in text


def test_docker_context_excludes_generated_artifacts():
    text = Path(".dockerignore").read_text()
    assert "out" in text
    assert "*.vcd" in text
    assert ".env" in text


def test_dockerfile_pins_base_image_digest():
    text = Path("docker/Dockerfile").read_text()
    assert "FROM python:3.10-slim@sha256:" in text
    assert "HOME=/tmp" in text
    assert "chmod 0777 /opt/agcws/out" in text
