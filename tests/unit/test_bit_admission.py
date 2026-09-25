import json
import shutil
from pathlib import Path

import pytest

from agcws.evidence.bit_bank import checked_trial, verify


@pytest.fixture
def checker():
    return checked_trial


def test_admission_recomputes_error(checker):
    trial = {"selected": True, "status": "MEASURED", "valid": True,
             "rates": [2.0]*8, "loss": .5}
    checker(trial, [1.0]*8, 2.0)
    with pytest.raises(ValueError, match="error differs"):
        checker({**trial, "loss": .1}, [1.0]*8, 2.0)


def test_admission_rejects_scored_invalid_and_filtered(checker):
    trial = {"selected": True, "status": "MEASURED", "valid": False, "loss": None}
    checker(trial, [1.0]*8, 2.0)
    with pytest.raises(ValueError, match="invalid attempt"):
        checker({**trial, "loss": 0}, [1.0]*8, 2.0)
    with pytest.raises(ValueError, match="filter"):
        checker({**trial, "selected": False}, [1.0]*8, 2.0)


def test_published_bit_archive_reproduces_and_rejects_changed_bank(monkeypatch, tmp_path):
    assert verify(Path('results/aes/tasks'))['qualified'] == 18
    for name in ("inputs.json.gz", "bank.json"):
        shutil.copy2(Path("results/aes/tasks") / ("calibration/" + name if name.endswith(".gz") else name), tmp_path / name)
    assert verify(tmp_path)["qualified"] == 18
    bank = json.loads((tmp_path / "bank.json").read_text())
    bank["admission"]["qualified"] = 17
    (tmp_path / "bank.json").write_text(json.dumps(bank))
    with pytest.raises(ValueError, match="published bank"):
        verify(tmp_path)
