"""Preparation/receipt checks, deliberately not claims of a gate simulation."""

import json
from pathlib import Path

import pytest

from agcws.designs.redmule import gls


def workload():
    return dict(size=16, pattern="random", data_seed=7,
                phases=[dict(start=2000, duration=1, jobs=1)])


def completion(cycles=65536):
    return ("AGCWS_REDMULE_JOB job=0 cycle=5000 errors=0\n"
            "[TB] - errors=00000000\n"
            f"AGCWS_REDMULE_WINDOW_DONE cycles={cycles}\n")


@pytest.mark.parametrize("cycles", [65536, 262144])
def test_reference_work_and_window(cycles):
    result = gls.validate_completion(completion(cycles), workload(), cycles)
    assert result["useful_work"] == 4096
    assert result["checked_outputs"] == 256


@pytest.mark.parametrize("old,new", [
    ("errors=0\n", "errors=1\n"), ("job=0", "job=1"), ("cycle=5000", "cycle=1999"),
    ("cycle=5000", "cycle=65536"), ("cycles=65536", "cycles=262144"),
    ("[TB] - errors=00000000", "[TB] - errors=00000001"),
    ("AGCWS_REDMULE_JOB", "MISSING_JOB"),
])
def test_reject_bad_reference(old, new):
    with pytest.raises(ValueError, match="record differs"):
        gls.validate_completion(completion().replace(old, new), workload(), 65536)


def test_duplicate_jobs_and_low_work_rejected():
    with pytest.raises(ValueError):
        gls.validate_completion(completion() + "AGCWS_REDMULE_JOB job=0 cycle=5001 errors=0\n",
                                workload(), 65536)
    with pytest.raises(ValueError, match="1024"):
        gls.validate_completion(completion(), {**workload(), "size": 4}, 65536)


def test_flat_boundary_and_original_memory_cpu_preserved():
    source = Path("benchmarks/redmule/target/sim/src/redmule_tb.sv").read_text()
    harness = gls.gate_testbench(source)
    assert "redmule_mm_wrap #(" not in harness
    assert f"{gls.TOP} i_redmule_wrap" in harness
    assert "cv32e40p_core #(" in harness
    assert harness[harness.index("  tb_dummy_memory"):].replace(
        "    reference_done = 1;", "    $finish;") == source[source.index("  tb_dummy_memory"):]
    for key in gls.TCDM:
        assert f".tcdm_{key}(redmule_tcdm.{key})" in harness
    top = gls.synthesis_top()
    assert ".DataW(128)" in top and ".Height(4)" in top and ".Width(4)" in top
    assert ".LatchBuffers(0)" in top and "DW:160" in top
    assert "input wire [159:0] tcdm_r_data" in top
    assert "assign target.req = target_req;" in top
    assert "assign tcdm_req = tcdm.req;" in top


def test_source_mapping_includes_header_hashes_and_fails_unknown(tmp_path):
    deps = tmp_path / "deps"
    deps.mkdir()
    (deps / "a.sv").write_text("module a; endmodule\n")
    inc = deps / "inc"
    inc.mkdir()
    (inc / "a.svh").write_text("// header\n")
    source = tmp_path / "sources.vlt"
    source.write_text("+define+PACE_ENABLED\n+incdir+/workspace/.dependencies/inc\n"
                      "/workspace/.dependencies/a.sv\n")
    lines, files = gls.resolve_sources(source, deps)
    assert str(deps / "a.sv") in lines
    assert inc / "a.svh" in files
    source.write_text("-f hidden.vlt\n")
    with pytest.raises(ValueError, match="unresolved"):
        gls.resolve_sources(source, deps)


def test_mapped_contract_rejects_blackboxes_and_memories(tmp_path):
    path = tmp_path / "mapped.json"
    top = {"ports": {name: dict(direction=direction, bits=list(range(width)))
                     for name, (direction, width) in gls.ports().items()},
           "cells": {"gate": {"type": "real_cell"}}}
    def save():
        path.write_text(json.dumps({"modules": {gls.TOP: top}}))
    save()
    assert gls.validate_mapped(path, ["real_cell"]) == 1
    with pytest.raises(ValueError, match="unsupported"):
        gls.validate_mapped(path, [])
    top["memories"] = {"memory": {}}
    save()
    with pytest.raises(ValueError, match="memory"):
        gls.validate_mapped(path, ["real_cell"])
    del top["memories"]
    top["ports"]["tcdm_r_data"]["bits"].pop()
    save()
    with pytest.raises(ValueError, match="port contract"):
        gls.validate_mapped(path, ["real_cell"])


def waveform(period=1000):
    return f"""$timescale 1ps $end
$scope module redmule_tb_wrap $end
$var wire 1 ! clk $end
$scope module i_redmule_tb $end
$var wire 1 ! clk_i $end
$var wire 1 r data_req $end
$var wire 1 g data_gnt $end
$var wire 1 w data_we $end
$var wire 32 a data_addr $end
$upscope $end
$upscope $end
$enddefinitions $end
#0
0!
1r
1g
1w
b100000000000000000000 a
#{period//2}
1!
#{period}
0!
0r
#{period+period//2}
1!
#{period+period//2+1}
"""


def test_waveform_bounds_are_not_ten_ns(tmp_path):
    path = tmp_path / "activity.vcd"
    path.write_text(waveform())
    bounds = gls.waveform_bounds(path, 2)
    assert bounds["clock_period_ps"] == 1000
    assert bounds["first_rising_edge_ps"] == 500
    assert bounds["last_rising_edge_ps"] == 1500
    assert bounds["harness_finish_ps"] == 1501
    assert bounds["accepted_trigger_edges"] == [1]
    path.write_text(waveform(10000))
    with pytest.raises(ValueError, match="period/phase"):
        gls.waveform_bounds(path, 2)


def test_waveform_wrong_timescale_and_truncated_clock(tmp_path):
    path = tmp_path / "activity.vcd"
    path.write_text(waveform().replace("1ps", "1ns"))
    with pytest.raises(ValueError, match="1ps"):
        gls.waveform_bounds(path, 2)
    path.write_text(waveform())
    with pytest.raises(ValueError, match="edge count"):
        gls.waveform_bounds(path, 3)


def test_dispatcher_contract_is_returned_only_after_replay(tmp_path, monkeypatch):
    from agcws.designs.redmule import matched

    rtl, synthesis, out = (tmp_path / name for name in ("rtl", "synthesis", "out"))
    rtl.mkdir()
    synthesis.mkdir()
    model = tmp_path / "cells.v"
    model.write_text("// fixture, never used for gate simulation\n")
    monkeypatch.setenv("AGCWS_SKY130_CELL_MODELS", str(model))
    monkeypatch.setenv("AGCWS_SKY130_PRIMITIVES", str(model))
    monkeypatch.setenv("AGCWS_REDMULE_FROZEN_RECEIPT", "/must/not/be/read")
    monkeypatch.setattr(matched, "synthesis_manifest", lambda _: {})
    def failed(*args):
        raise ValueError("reference mismatch")
    monkeypatch.setattr(gls, "replay", failed)
    with pytest.raises(ValueError, match="reference mismatch"):
        matched.replay_trial(rtl, synthesis, out)
    assert not (out / "matched_replay.json").exists()
    def fixture_replay(*args):
        assert args[-1] == frozen
        out.mkdir()
        gls.write_json(out / "gls_receipt.json", {"window": {"clock_edges": 65536}})
    monkeypatch.setattr(gls, "replay", fixture_replay)
    frozen = tmp_path / "replay-receipt.json"
    frozen.write_text("{}")
    receipt = matched.replay_trial(rtl, synthesis, out, frozen_receipt=frozen)
    assert receipt["clock"] == receipt["rtl_clock"] == gls.CLOCK
    assert receipt["scope"] == "redmule_tb_wrap/i_redmule_tb/i_redmule_wrap"
    assert receipt["clock_port"] == "clk_i"
    assert receipt["bounds"] is None
    assert receipt["expected_period_s"] == 1e-9
