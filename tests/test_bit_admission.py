import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest


@pytest.fixture
def checker(monkeypatch):
    monkeypatch.syspath_prepend(str(Path("analysis").resolve()))
    spec = importlib.util.spec_from_file_location("bit_admission_test", "analysis/admit_bit_bank.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module.checked_trial


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
    monkeypatch.syspath_prepend(str(Path("analysis").resolve()))
    spec = importlib.util.spec_from_file_location("bit_archive_test", "analysis/verify_bit_archive.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("inputs.json.gz", "bank.json"):
        shutil.copy2(Path("results/aes/bit-activity-v2") / name, tmp_path / name)
    assert module.verify(tmp_path)["qualified"] == 18
    bank = json.loads((tmp_path / "bank.json").read_text())
    bank["admission"]["qualified"] = 17
    (tmp_path / "bank.json").write_text(json.dumps(bank))
    with pytest.raises(ValueError, match="published bank"):
        module.verify(tmp_path)
