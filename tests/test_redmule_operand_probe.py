import runpy


def test_operand_grid_preserves_timing_and_size_and_counts_duplicates():
    program = {"size": 16, "pattern": "zeros", "data_seed": 0,
               "phases": [{"start": 100, "duration": 1, "jobs": 1}]}
    rows = [{"id": str(i), "qualified": i >= 7, "program": program} for i in range(18)]
    cases = runpy.run_path("analysis/redmule_operand_probe.py")["cases"](rows)
    assert len(cases) == len({c["id"] for c in cases}) == 354
    assert all(c["program"]["size"] == 16 and c["program"]["phases"] == program["phases"] for c in cases)
    assert cases[0]["program"] == cases[1]["program"]
    assert program["pattern"] == "zeros" and program["data_seed"] == 0
