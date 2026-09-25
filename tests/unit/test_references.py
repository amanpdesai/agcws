"""Portable publication checks; no simulations or ignored-out dependencies."""
import shutil
from pathlib import Path

import pytest

from agcws.reporting.references import DESIGNS, check_join, verify


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
    if not (root / "results/aes/tasks/references").exists():
        pytest.skip("Published reference evidence not installed")
    (tmp_path / 'results').mkdir()
    shutil.copy2(root / 'results/index.json', tmp_path / 'results/index.json')
    for design in DESIGNS:
        for kind in ("tasks/references", "power/validation"):
            relative = Path("results") / design / kind
            shutil.copytree(root / relative, tmp_path / relative)
        archive = Path('results') / design / 'power/measurements.jsonl.gz'
        shutil.copy2(root / archive, tmp_path / archive)
    # No out directory or frozen execution workspace is required.
    assert verify(tmp_path) == {"verified_native_measurements": 40}
    path = tmp_path / 'results/aes/tasks/references/evidence.json.gz'
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match='hash mismatch'):
        verify(tmp_path)
