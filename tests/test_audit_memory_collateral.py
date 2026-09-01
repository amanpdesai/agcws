import json
from pathlib import Path

import pytest

from scripts.audit_memory_collateral import audit
from scripts.generate_memory_collateral import generate


def test_audit_memory_collateral_accepts_generated_bundle(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"top": "fifo", "memories": [
        {"module": "fifo", "name": "r", "width": 8, "size": 256,
         "abits": 8, "rd_ports": 1, "wr_ports": 0,
         "parameters": {"RD_CLK_ENABLE": "1"}},
    ]}))
    directory = tmp_path / "collateral"
    generate(inventory, directory)
    result = audit(directory)
    assert result["valid"] is True
    assert result["mapping_ready"] is True


def test_audit_memory_collateral_accepts_empty_inventory(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"top": "aes", "memories": []}))
    directory = tmp_path / "collateral"
    generate(inventory, directory)
    result = audit(directory)
    assert result["valid"] is True
    assert result["macros"] == 0
    assert result["mapping_ready"] is False


def test_audit_memory_collateral_reports_stale_schema(tmp_path: Path):
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"top": "fifo", "memories": [
        {"module": "fifo", "name": "r", "width": 8, "size": 256,
         "abits": 8, "rd_ports": 1, "wr_ports": 0},
    ]}))
    directory = tmp_path / "collateral"
    generate(inventory, directory)
    manifest = json.loads((directory / "memory-macros.json").read_text())
    del manifest["macros"][0]["mapping_eligible"]
    (directory / "memory-macros.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="missing mapping_eligible"):
        audit(directory)
