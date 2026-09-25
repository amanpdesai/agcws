import copy
import runpy
import struct

import pytest

from agcws.core.contracts import SimResult, ValidityStage
from agcws.designs.redmule.adapter import (
    RedmuleTemporalAdapter,
    reference_matrices,
    stimulus_headers,
)


def workload():
    return {"size": 8, "pattern": "random", "data_seed": 7100,
            "phases": [{"start": 8000, "duration": 16000, "jobs": 2}]}


def test_expansion_and_headers_are_deterministic_and_nonmutating():
    program = workload()
    original = copy.deepcopy(program)
    assert RedmuleTemporalAdapter().elaborate(program) == [8000, 16000]
    assert stimulus_headers(program) == stimulus_headers(program)
    assert program == original
    assert "uint32_t golden[32]" in stimulus_headers(program)["golden.h"]


@pytest.mark.parametrize("size", [4, 8, 16])
@pytest.mark.parametrize("pattern", ["zeros", "alternating", "random"])
def test_reference_matches_stepwise_fp16_accumulation(size, pattern):
    x, w, y, z = reference_matrices(size, pattern, 7100)
    for r in range(size):
        for c in range(size):
            acc = y[r*size+c]
            for k in range(size):
                acc = struct.unpack("<e", struct.pack("<e", acc + x[r*size+k]*w[k*size+c]))[0]
            assert acc == z[r*size+c]


def test_static_gates_and_dynamic_floor_are_distinct():
    adapter = RedmuleTemporalAdapter()
    program = workload()
    program["size"] = True
    assert adapter.validate_schema(program).stage == ValidityStage.SCHEMA
    program = workload()
    program["phases"][0]["duration"] = 65536
    assert adapter.validate_protocol(program).stage == ValidityStage.PROTOCOL
    assert adapter.validate_result(SimResult(True, True, True, 512)).stage == ValidityStage.USEFUL_WORK
    assert adapter.validate_result(SimResult(True, True, True, 1024)).valid
    assert adapter.validate_result(SimResult(False, True, True, 1024)).stage == ValidityStage.FUNCTIONAL


def test_rtl_cache_fingerprint_covers_include_headers_and_derived_harness(tmp_path, monkeypatch):
    hashes = runpy.run_path("src/agcws/designs/redmule/simulate.py")["source_hashes"]
    monkeypatch.setitem(hashes.__globals__, "ROOT", tmp_path)
    for name in ("src/agcws/designs/redmule/prepare.py", "src/agcws/designs/redmule/simulate.py",
                 "benchmarks/redmule/target/sim/src/redmule_tb.sv",
                 "benchmarks/redmule/target/sim/src/redmule_tb_wrap.sv", "includes/defines.svh", "dut.sv"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    source_list = tmp_path / "sources.vlt"
    source_list.write_text(f"+define+TEST\n+incdir+{tmp_path}/includes\n{tmp_path}/dut.sv\n")
    before = hashes(source_list)
    (tmp_path / "includes/defines.svh").write_text("changed")
    assert hashes(source_list) != before
    source_list.write_text("-unsupported-option\n")
    with pytest.raises(ValueError, match="unresolved source-list entry"):
        hashes(source_list)
