import json
import subprocess
from pathlib import Path
import pytest
from agcws.adapters.axi_dma.runtime import load_sim_result


def test_axi_dma_workload_drives_both_channels(tmp_path: Path):
    workload = tmp_path / "workload.json"
    workload.write_text(json.dumps({"transfers": [
        {"src": 0, "dst": 4096, "length": 1024},
        {"src": 1024, "dst": 5120, "length": 1024},
        {"src": 2048, "dst": 6144, "length": 1024},
        {"src": 3072, "dst": 7168, "length": 1024},
    ]}))
    result = subprocess.run([".venv/bin/python", "scripts/run_axi_dma_workload.py", str(workload), str(tmp_path / "out")],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "AGCWS_AXI_DMA_WORKLOAD_OK transfers=4" in result.stdout
    manifest = json.loads((tmp_path / "out/workload_manifest.json").read_text())
    assert manifest["simulation"]["useful_work"] == 4096
    assert manifest["simulation"]["outputs_ok"]
    assert len(manifest["provenance"]["rtl_commit"]) == 40
    assert manifest["provenance"]["workload_sha256"]
    assert manifest["provenance"]["tools"]["iverilog"]
    for direction in ("read", "write"):
        artifact = manifest["transfers"][0]["artifacts"][direction]
        assert len(artifact["sha256"]) == 64
        assert artifact["bytes"] > 0
        assert (tmp_path / "out" / artifact["path"]).is_file()
        assert artifact["clock_edges"] > 0
        assert artifact["total_transitions"] > 0
        assert (tmp_path / "out" / artifact["activity_path"]).is_file()
    assert load_sim_result(tmp_path / "out/workload_manifest.json").useful_work == 4096
    assert manifest["transfers"][0]["length"] == 1024


def test_axi_dma_workload_enforces_useful_work_floor(tmp_path: Path):
    workload = tmp_path / "workload.json"
    workload.write_text(json.dumps({"transfers": [{"src": 256, "dst": 512, "length": 64}]}))
    result = subprocess.run([".venv/bin/python", "scripts/run_axi_dma_workload.py", str(workload), str(tmp_path / "out")],
                            capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "USEFUL_WORK" in result.stderr


def test_dma_runtime_loader_rejects_incomplete_manifest(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"simulation": {"terminated": True}}))
    with pytest.raises(ValueError, match="incomplete"):
        load_sim_result(manifest)
