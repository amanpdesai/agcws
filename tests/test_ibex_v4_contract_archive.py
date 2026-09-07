import json
import shutil
from pathlib import Path

import pytest

from analysis.ibex_contract_v4 import verify


def test_complete_failed_gate_is_reproducible_and_not_ready():
    report = verify(Path("results/ibex_temporal_v4_contract"))
    assert report["calls_verified"] == 24
    assert report["slots_verified"] == 48
    assert not report["ready"]


def test_archive_rejects_changed_raw_response(tmp_path):
    root = tmp_path / "archive"
    shutil.copytree("results/ibex_temporal_v4_contract", root)
    path = root / "calls/target_0-600-original.json"
    value = json.loads(path.read_text())
    value["raw_text"] = "{}"
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="raw decoding"):
        verify(root)
