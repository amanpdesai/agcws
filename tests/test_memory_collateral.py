import json
from pathlib import Path

from scripts.generate_memory_collateral import generate


def test_memory_collateral_preserves_geometry(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({
        "top": "ram",
        "memories": [{"module": "ram", "name": "$mem", "width": 8,
                       "size": 256, "abits": 8, "rd_ports": 1, "wr_ports": 1}],
    }))
    result = generate(inventory, tmp_path / "collateral")
    assert result["mapping_ready"] is False
    assert result["macros"][0]["depth"] == 256
    assert result["macros"][0]["physical_depth"] == 256
    assert result["macros"][0]["physical_width"] == 8
    config = json.loads((tmp_path / "collateral/bsg_fakeram.json").read_text())
    assert config["srams"] == [{"name": "fakeram130_256x8", "width": 8,
                                 "depth": 256, "banks": 1}]
    assert "agcws_mem_0_mem" in (tmp_path / "collateral/memory_macros.v").read_text()


def test_memory_collateral_pads_small_physical_macros(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"top": "fifo", "memories": [
        {"module": "fifo", "name": "bits", "width": 1, "size": 32,
         "abits": 5, "rd_ports": 1, "wr_ports": 1},
    ]}))
    result = generate(inventory, tmp_path / "collateral")
    assert result["macros"][0]["depth"] == 32
    assert result["macros"][0]["physical_depth"] == 512
    assert result["macros"][0]["physical_width"] == 1
    config = json.loads((tmp_path / "collateral/bsg_fakeram.json").read_text())
    assert config["srams"][0]["depth"] == 512


def test_memory_collateral_pads_non_power_of_two_width(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"top": "fifo", "memories": [
        {"module": "fifo", "name": "tag", "width": 20, "size": 32,
         "abits": 5, "rd_ports": 1, "wr_ports": 1},
    ]}))
    result = generate(inventory, tmp_path / "collateral")
    assert result["macros"][0]["physical_width"] == 32
    config = json.loads((tmp_path / "collateral/bsg_fakeram.json").read_text())
    assert config["srams"][0]["width"] == 32


def test_memory_collateral_deduplicates_macro_geometries(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"top": "dma", "memories": [
        {"module": "dma", "name": "a", "width": 8, "size": 32, "abits": 5,
         "rd_ports": 1, "wr_ports": 1},
        {"module": "dma", "name": "b", "width": 8, "size": 32, "abits": 5,
         "rd_ports": 1, "wr_ports": 1},
    ]}))
    result = generate(inventory, tmp_path / "collateral")
    assert len(result["macros"]) == 1
    assert len(json.loads((tmp_path / "collateral/bsg_fakeram.json").read_text())["srams"]) == 1
