import runpy

import pytest

module = runpy.run_path("analysis/audit_witness_refinement.py")


@pytest.mark.parametrize("cases,qualified", [(18, 17), (9, 9), (0, 0)])
def test_partial_bank_never_admitted(tmp_path, monkeypatch, cases, qualified):
    monkeypatch.setitem(module["admitted_bank"].__globals__, "analyze",
                        lambda root: {"cases": cases, "qualified": qualified})
    with pytest.raises(ValueError, match="both nine-request splits"):
        module["admitted_bank"](tmp_path)
