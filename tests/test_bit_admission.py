import importlib.util
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
