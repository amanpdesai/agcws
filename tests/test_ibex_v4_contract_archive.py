import json
import shutil
from pathlib import Path

import pytest

from analysis.ibex_contract_v4 import verify


@pytest.mark.parametrize(
    "directory,ready",
    [
        ("ibex_temporal_v4_contract", False),
        ("ibex_temporal_v4_contract_v2", True),
    ],
)
def test_complete_contract_gate_is_reproducible(directory, ready):
    report = verify(Path("results") / directory)
    assert report["calls_verified"] == 24
    assert report["slots_verified"] == 48
    assert report["ready"] == ready


def test_archive_rejects_changed_raw_response(tmp_path):
    root = tmp_path / "archive"
    shutil.copytree("results/ibex_temporal_v4_contract", root)
    path = root / "calls/target_0-600-original.json"
    value = json.loads(path.read_text())
    value["raw_text"] = "{}"
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="raw decoding"):
        verify(root)
