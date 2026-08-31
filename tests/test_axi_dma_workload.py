import json
import subprocess
from pathlib import Path


def test_axi_dma_workload_drives_both_channels(tmp_path: Path):
    workload = tmp_path / "workload.json"
    workload.write_text(json.dumps({"transfers": [{"src": 256, "dst": 512, "length": 64}]}))
    result = subprocess.run([".venv/bin/python", "scripts/run_axi_dma_workload.py", str(workload), str(tmp_path / "out")],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "AGCWS_AXI_DMA_WORKLOAD_OK transfers=1" in result.stdout
    assert (tmp_path / "out/workload_manifest.json").is_file()
