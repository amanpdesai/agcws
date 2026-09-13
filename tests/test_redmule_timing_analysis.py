import runpy

import pytest

from agcws.pipeline.storage import write

module = runpy.run_path("analysis/redmule_timing.py")
job_metrics, analyze = module["job_metrics"], module["analyze"]


def fixture():
    program = {"size": 8, "pattern": "zeros", "data_seed": 0,
               "phases": [{"start": 8000, "duration": 100, "jobs": 2}]}
    functional = {"valid": True, "completed_jobs": 2, "useful_work": 1024,
                  "checked_outputs": 128, "job_completions": [[0, 9000, 0], [1, 10000, 0]]}
    return program, functional


def test_timing_separates_previous_completion_from_remaining_interval():
    rows = job_metrics(*fixture())
    assert rows[0]["release_to_completion_cycles"] == 1000
    assert rows[1]["previous_completion_after_release_cycles"] == 950
    assert rows[1]["remaining_after_eligibility_cycles"] == 1000
    assert all(r["crossed_requested_bin"] for r in rows)


@pytest.mark.parametrize("jobs", [[[0, 7999, 0], [1, 10000, 0]],
                                 [[0, 9000, 0], [1, 8500, 0]],
                                 [[0, 9000, 0], [1, 65536, 0]],
                                 [[0, 9000, 1], [1, 10000, 0]]])
def test_bad_completion_records_fail_closed(jobs):
    program, functional = fixture()
    functional["job_completions"] = jobs
    with pytest.raises(ValueError, match="completion"):
        job_metrics(program, functional)


def test_reference_work_mismatch_fails_closed():
    program, functional = fixture()
    functional["checked_outputs"] = 1
    with pytest.raises(ValueError, match="functional"):
        job_metrics(program, functional)


def test_panel_audit_counts_rejections_but_deduplicates_measured_work(tmp_path):
    program, functional = fixture()
    write(tmp_path / "manifest.json", {"spec": {"domain": "redmule-temporal"}})
    write(tmp_path / "complete.json", {"slots": 3})
    valid = {"valid": True, "cache_id": "same", "program": program}
    write(tmp_path / "panel/t/1/phase-ga/batches/001/trials.json",
          [valid, valid, {"valid": False, "stage": "USEFUL_WORK"}])
    write(tmp_path / "cache/same/result.json", {"valid": True})
    write(tmp_path / "cache/same/attempt-001/program.json", program)
    write(tmp_path / "cache/same/attempt-001/functional.json", functional)
    result = analyze(tmp_path)
    assert result["proposal_slots"] == 3
    assert result["unique_valid_workloads"] == 1
    assert result["invalid_slots_by_stage"] == {"USEFUL_WORK": 1}
    assert result["groups"]["size_8/zeros"]["jobs"] == 2
    write(tmp_path / "cache/same/attempt-002/program.json", program)
    write(tmp_path / "cache/same/attempt-002/functional.json", functional)
    with pytest.raises(ValueError, match="ambiguous"):
        analyze(tmp_path)
