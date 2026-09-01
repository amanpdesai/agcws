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
    config = json.loads((tmp_path / "collateral/bsg_fakeram.json").read_text())
    assert config["srams"] == [{"name": "fakeram130_256x8", "width": 8,
                                 "depth": 256, "banks": 1}]
    assert "agcws_mem_0_mem" in (tmp_path / "collateral/memory_macros.v").read_text()
