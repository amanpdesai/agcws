import runpy

from agcws.pipeline.ibex.program import allocation, canonical


def test_operation_probe_fixed_legal_work_and_unique_cases():
    rows = runpy.run_path("analysis/ibex_operation_probe.py")["cases"]()
    assert len(rows) == len({r["id"] for r in rows}) == 88
    for row in rows:
        program = canonical(row["program"])
        assert allocation(program) == [4096]
        assert program["segments"][0]["release"] == 0
