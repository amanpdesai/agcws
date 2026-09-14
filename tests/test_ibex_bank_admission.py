import runpy

import pytest

from agcws.pipeline.targets import qualify, requests


def fixture():
    bank = {"calibration": {"scale": 10}, "splits": {}}
    rows, reports = [], []
    for split in ("development", "confirmation"):
        requested = requests(0, 10, split=split)
        bank["splits"][split] = {"requests": requested}
        for request in requested:
            name = f"{split}-{request['id']}"
            witness = {"valid": True, "rates": request["rates"]}
            for index in range(12):
                rows.append({"id": f"{name}-{index:02}", "request_id": name,
                             "program": {"placeholder": index}, "measurement": {
                                 "valid": True, "profile": {"window_rates": request["rates"]}}})
            reports.append({"id": name, "witness_case": f"{name}-00",
                            **qualify(request, witness, scale=10, tolerance=.1, nonflat_margin=.02)})
    return {"bank": bank}, {"charged_slots": 216, "results": rows, "reports": reports}


def test_selection_matches_frozen_tie_break_and_rejects_tamper():
    select = runpy.run_path("analysis/ibex_bank_admission.py")["select"]
    config, complete = fixture()
    selected = select(config, complete)
    assert len(selected) == 18
    assert all(c["program"] == {"placeholder": 0} for c in selected)
    complete["reports"][0]["qualified"] = False
    with pytest.raises(ValueError):
        select(config, complete)


def test_incomplete_original_panel_rejected():
    select = runpy.run_path("analysis/ibex_bank_admission.py")["select"]
    config, complete = fixture()
    complete["results"].pop()
    with pytest.raises(ValueError):
        select(config, complete)
