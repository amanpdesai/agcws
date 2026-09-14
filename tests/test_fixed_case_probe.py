import runpy

import pytest

from agcws.workloads.schedule import ScheduleContract, expand_schedule

probe = runpy.run_path("scripts/probe_fixed_cases.py")
config = runpy.run_path("analysis/dma_timing_probe.py")["config"]


def test_twelve_corner_cases_preserve_resources_and_cover_depth_and_placement():
    cases = probe["validate"](config())["cases"]
    assert len(cases) == 12
    assert len({case["id"] for case in cases}) == 12
    for case in cases:
        sequence = expand_schedule(case["program"], ScheduleContract(64, 6000))
        depth = int(case["id"].split("-")[1])
        assert {node["units"] for node in sequence if node["op"] == "work"} == {depth}


@pytest.mark.parametrize("name", ["../escape", "", ".", "a/b"])
def test_unsafe_case_path_rejected(name):
    value = config()
    value["cases"][0]["id"] = name
    with pytest.raises(ValueError):
        probe["validate"](value)


def test_duplicate_case_id_rejected():
    value = config()
    value["cases"].append(value["cases"][0])
    with pytest.raises(ValueError, match="unique"):
        probe["validate"](value)
