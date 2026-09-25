import copy
import gzip
import json
from pathlib import Path

import pytest

from agcws.evaluation.power.mesh_sensitivity import restrict
from agcws.reporting.mesh_sensitivity import verify

EVIDENCE = Path("results/mesh/sink-sensitivity")


@pytest.mark.parametrize("pause,expected", [(-2, 0), (0, 0), (2, 2), (3, 3), (9, 3)])
def test_restrict_only_sink_fields(pause, expected):
    original = {"sink_period": 20, "sink_pause": pause, "phases": [{"packets": 5}]}
    snapshot = copy.deepcopy(original)
    result = restrict(original)
    assert original == snapshot
    assert result == {**snapshot, "sink_period": 8, "sink_pause": expected}
    result["phases"][0]["packets"] = 99
    assert original == snapshot


def test_published_sensitivity_is_reproducible():
    result = verify(EVIDENCE)
    assert result == json.loads((EVIDENCE / "summary.json").read_text())
    assert result["total"] == 180 and result["changed"] == 16
    flash, strong = (result["by_arm"][arm] for arm in ("flash-lite-medium", "strong-medium-64k"))
    assert flash["nonflat"]["restricted_solved"] == flash["nonflat"]["original_solved"] == 20
    assert strong["nonflat"]["restricted_solved"] == strong["nonflat"]["original_solved"] == 80
    assert flash["controls"]["lost_matches"] == 1


def test_tampered_native_evidence_rejected(tmp_path):
    record = json.loads(gzip.decompress((EVIDENCE / "evidence.json.gz").read_bytes()))
    record["files"]["summary.json"]["text"] += " "
    (tmp_path / "evidence.json.gz").write_bytes(gzip.compress(json.dumps(record).encode()))
    with pytest.raises(ValueError, match="checksum differs"):
        verify(tmp_path)
