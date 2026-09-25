"""Portable publication checks; no simulations or ignored-out dependencies."""
import json
import shutil
from pathlib import Path

import pytest

from agcws.reporting.reference_repair import DESIGNS, check_join, put, verify


def test_publication_refuses_overwrite(tmp_path):
    path = tmp_path / "measurement.json"
    put(path, b"native\n")
    put(path, b"native\n")
    with pytest.raises(AssertionError):
        put(path, b"changed")
    assert path.read_bytes() == b"native\n"


def test_join_rejects_other_program():
    case = dict(program={"x": 1}, rates=[1], target_rates=[1], scale=1,
                max_bin_error=0, target="t")
    activity = dict(case, activity_solved=True)
    check_join(case, {"activity": activity})
    activity["program"] = {"x": 2}
    with pytest.raises(AssertionError):
        check_join(case, {"activity": activity})


def test_portable_bank_and_tamper_detection(tmp_path):
    root = Path(__file__).resolve().parents[2]
    if not (root / "results/aes/tasks/repaired-references-v1").exists():
        pytest.skip("Published reference evidence not installed")
    for design in DESIGNS:
        for kind in ("tasks", "power"):
            relative = Path("results") / design / kind / "repaired-references-v1"
            shutil.copytree(root / relative, tmp_path / relative)
    # No out directory, original archives, or frozen workspace required.
    assert verify(tmp_path) == {"verified_native_measurements": 40}
    index = json.loads((tmp_path / "results/aes/power/repaired-references-v1/index.json").read_bytes())
    path = tmp_path / next(iter(index["references"].values()))["path"]
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(AssertionError):
        verify(tmp_path)
