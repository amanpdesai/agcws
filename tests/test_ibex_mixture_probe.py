import runpy

from agcws.pipeline.ibex.program import allocation


def test_mixtures_keep_native_work_and_source_operands():
    cases = runpy.run_path("analysis/ibex_mixture_probe.py")["cases"]()
    assert len(cases) == len({c["id"] for c in cases}) == 24
    for case in cases:
        p = case["program"]
        assert allocation(p) == [4096]
        body = p["segments"][0]["body"]
        assert len(body) == 8
        assert all(i["a"] == 0 and i["b"] == 1 and i["dst"] == 7 for i in body)
