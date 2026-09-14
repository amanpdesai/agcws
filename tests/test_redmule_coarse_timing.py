import runpy


def test_coarse_moves_are_unrepaired_and_keep_other_fields():
    p = {"size": 16, "pattern": "zeros", "data_seed": 0,
         "phases": [{"start": 0, "duration": 1, "jobs": 1}]}
    rows = runpy.run_path("analysis/redmule_coarse_timing.py")["proposals"](p)
    assert len(rows) == 8
    assert {r["phases"][0]["start"] for r in rows} == {-8192,8192,-4096,4096,-2048,2048,-1024,1024}
    assert all(r["phases"][0]["jobs"] == 1 and r["size"] == 16 for r in rows)
    assert p["phases"][0]["start"] == 0
