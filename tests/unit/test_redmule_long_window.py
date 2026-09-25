import random
from pathlib import Path

import pytest

from agcws.designs.redmule.adapter import RedmuleTemporalAdapter, stimulus_headers
from agcws.designs.temporal_registry import backend


def test_windows_are_explicit_and_isolated():
    short = RedmuleTemporalAdapter()
    long = RedmuleTemporalAdapter(262144)
    workload = {"size": 16, "pattern": "zeros", "data_seed": 0,
                "phases": [{"start": 200000, "duration": 1000, "jobs": 1}]}
    assert not short.validate_schema(workload).valid
    assert long.validate_schema(workload).valid
    assert long.elaborate(workload) == [200000]
    assert "200000" in stimulus_headers(workload, observation_cycles=262144)["workload.h"]
    assert all("65536" not in line for line in long.protocol_constraints)
    workload["phases"][0]["duration"] = 62145
    assert not long.validate_protocol(workload).valid
    assert short.workload_schema == RedmuleTemporalAdapter.workload_schema


@pytest.mark.parametrize("cycles", [True, 65536.0, 131072, 0])
def test_undeclared_windows_rejected(cycles):
    with pytest.raises(ValueError):
        RedmuleTemporalAdapter(cycles)


def test_long_backend_native_contract():
    design = backend("redmule-temporal-long")
    assert design.clock_edges == 262144
    assert backend("redmule-temporal").clock_edges == 65536
    rng = random.Random(7200)
    programs = [design.random(rng) for _ in range(64)]
    assert any(p["phases"][-1]["start"] > 65536 for p in programs)
    assert any(sum(s["jobs"] for s in p["phases"]) > 12 for p in programs)
    for program in programs:
        assert design.adapter().validate_schema(program).valid
        assert design.adapter().validate_protocol(program).valid
    invocation = design.invocation(programs[0], Path("unused"), Path("attempt"))
    assert invocation[-2:] == ["--observation-cycles", "262144"]
