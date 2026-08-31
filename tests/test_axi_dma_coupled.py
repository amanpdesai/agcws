from pathlib import Path
import json
import shutil
import subprocess
import sys

import pytest


@pytest.mark.skipif(shutil.which("fst2vcd") is None,
                    reason="full coupled waveform regression requires fst2vcd")
def test_coupled_dma_produces_verified_activity_manifest(tmp_path: Path):
    result = subprocess.run(
        ["bash", "scripts/run_axi_dma_coupled.sh",
         "experiments/workloads/axi_dma_smoke.json", str(tmp_path)],
        env={**__import__("os").environ, "AGCWS_PYTHON": sys.executable},
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr[-4000:]
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["coupled_axi_dma_top"] is True
    assert manifest["useful_work_bytes"] == 4096
    assert (tmp_path / "activity.vcd").is_file()
    assert (tmp_path / "activity.json").is_file()
