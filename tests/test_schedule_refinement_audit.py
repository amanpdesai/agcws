import hashlib
import runpy

import pytest

from agcws.pipeline.metrics import key
from agcws.pipeline.storage import write
from agcws.workloads.schedule import ScheduleContract

audit = runpy.run_path("analysis/audit_schedule_refinement.py")
helper = runpy.run_path("analysis/schedule_refinement.py")


def fixture(root, monkeypatch):
    class Design:
        contract = ScheduleContract(64, 6000)
        clock_edges = 6774
        scope = "aes_core_smoke.dut"
        canonical = staticmethod(lambda program: program)
        completed = staticmethod(lambda attempt: {"valid": True})

    namespace = audit["analyze"].__globals__
    monkeypatch.setitem(namespace, "backend", lambda name: Design())
    monkeypatch.setitem(namespace, "source_inventory", lambda *args: {})
    bank = {"procedure": "test", "calibration": {"scale": 1, "low": 0}, "splits": {}}
    cases, reports = [], []
    for split in ("development", "confirmation"):
        requests = []
        for index in range(9):
            control = index == 8
            rates = [1]*8 if control else [0, 1]*4
            request = {"id": str(index), "control": control, "rates": rates}
            requests.append(request)
            program = {"sequence": [{"op": "wait", "cycles": index+1},
                                    {"op": "work", "units": 64},
                                    {"op": "wait", "cycles": 5999-index}]}
            identifier = key({"program": program, "measurement": "test"})
            result = {"valid": True, "cache_id": identifier, "rates": rates,
                      "profile": {"window_rates": rates, "useful_work": 64,
                                  "scope": Design.scope, "fidelity": "activity"}}
            cache = root / "cache" / identifier
            if not cache.exists():
                write(cache / "result.json", result)
                write(cache / "attempt-001/program.json", program)
                samples = [r for i, r in enumerate(rates) for _ in range((i+1)*6774//8-i*6774//8)]
                write(cache / "attempt-001/activity.json", {"clock_edges": 6774, "per_cycle_toggles": samples})
            case = {"id": f"{split}-{index}", "request": request, "program": program, "rates": rates,
                    "seed": 8300 if split == "development" else 8400,
                    "initial_candidates": helper["initial_schedules"](rates, 0, Design.contract, 6774)}
            cases.append(case)
            directory = root / "panel" / case["id"]
            write(directory / "initial.json", {"program": program, "measurement": result})
            report = {"id": case["id"], "charged_slots": 1, "budget": 260,
                      "program": program, "measurement": result,
                      "qualified": True, "reasons": [], "witness_error": 0.0}
            write(directory / "complete.json", report)
            reports.append(report)
        bank["splits"][split] = {"requests": requests, "pairwise_distances": []}
    write(root / "manifest.json", {"kind": "aes-schedule-witness-refinement-v3", "domain": "aes-temporal",
                                   "budget": 260, "paired_batches": 128, "bank": bank,
                                   "measurement": {"sources": {}, "measurement_fingerprint": "test"},
                                   "driver_sources": runpy.run_path("scripts/refine_schedule_witnesses.py")["sources"](),
                                   "cases": cases})
    digest = hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()
    write(root / "freeze.json", {"manifest_sha256": digest})
    write(root / "complete.json", {"kind": "aes-schedule-witness-refinement-v3", "reports": reports})
    return root / "cache" / key({"program": cases[0]["program"], "measurement": "test"})


def test_complete_bank_reconstructs_and_public_bank_hides_programs(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch)
    result = audit["analyze"](tmp_path)
    assert result["qualified"] == result["charged_slots"] == 18
    public = audit["admitted_bank"](tmp_path)
    assert public["full_study_ready"] is False
    assert "program" not in str(public)


def test_changed_activity_is_not_accepted_as_measured_evidence(tmp_path, monkeypatch):
    cache = fixture(tmp_path, monkeypatch)
    path = cache / "attempt-001/activity.json"
    original_read = audit["analyze"].__globals__["read"]

    def changed_read(p):
        value = original_read(p)
        if p == path:
            value["per_cycle_toggles"][0] += 1
        return value

    monkeypatch.setitem(audit["analyze"].__globals__, "read", changed_read)
    with pytest.raises(ValueError, match="does not reconstruct"):
        audit["analyze"](tmp_path)


def test_extra_proposals_after_success_are_rejected(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch)
    write(tmp_path / "panel/development-0/seeds.json", {})
    with pytest.raises(ValueError, match="after qualification"):
        audit["analyze"](tmp_path)


@pytest.mark.parametrize("count", [0, 9, 17])
def test_partial_bank_never_admitted(tmp_path, monkeypatch, count):
    monkeypatch.setitem(audit["admitted_bank"].__globals__, "analyze", lambda root: {"cases": 18, "qualified": count})
    with pytest.raises(ValueError, match="both controls"):
        audit["admitted_bank"](tmp_path)
