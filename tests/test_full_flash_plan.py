import json
import runpy

from agcws.pipeline.storage import read


def test_full_flash_plan_is_matched_and_excludes_private_witnesses():
    config = runpy.run_path("scripts/prepare_full_flash.py")["config"]
    bank = read("results/dma/qualified-bank-v6.json")
    bank["private"] = "DO_NOT_SEND_WITNESSES"
    manifest = read("results/dma/transport-bridge-v1/manifest.json")
    result = config(bank, manifest)
    assert result["seeds"] == list(range(9100, 9110))
    assert len(result["targets"]) == 9
    assert all(n.startswith("confirmation-") for n in result["targets"])
    assert result["budget"] == 128 and result["batch_size"] == 2
    assert result["stop_on_success"] is True
    assert result["policies"] == ["flash-4096", "phase-random", "phase-ga"]
    assert result["cost_ceiling_usd"] == 120
    assert "DO_NOT_SEND_WITNESSES" not in json.dumps(result)
