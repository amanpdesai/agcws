import runpy

import pytest

from agcws.pipeline.storage import write


def test_qualification_refuses_incomplete_panel(tmp_path):
    write(tmp_path / "manifest.json", {"measurement": {"measurement_fingerprint": "same"},
                                       "config": {"cases": []}})
    write(tmp_path / "complete.json", {"results": [], "charged_slots": 0})
    bank = {"calibration": {"measurement_fingerprint": "same"}}
    with pytest.raises(ValueError, match="486-slot"):
        runpy.run_path("analysis/qualify_redmule_bins.py")["audit"](tmp_path, bank)
