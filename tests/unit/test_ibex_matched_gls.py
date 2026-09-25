import json
from pathlib import Path

import pytest

from agcws.designs.ibex.gls import (
    ASSETS,
    PARAMETERS,
    checked_reference,
    closure,
    compare_retirement,
    marker_bounds,
    system_harness,
    tracing_harness,
    verify_hashes,
    yosys_path,
)
from agcws.designs.ibex.programs.program import HORIZON


def test_gate_harness_generates_a_real_reset_assertion_edge():
    harness = (ASSETS / 'gls.sv').read_text()
    assert 'bit rst_n = 1;' in harness
    assert '#1 rst_n = 0;' in harness
    assert '#7 rst_n = 1;' in harness


def test_ibex_gls_marker_window_is_retired_start_not_entire_waveform():
    found = {"measure_start": {"tick": 286}, "body_complete": {"tick": 2000},
             "measure_stop": {"tick": 400420}}
    assert marker_bounds(found) == [286, 286 + 2 * HORIZON]
    for name, tick in [("body_complete", 286), ("body_complete", 400286),
                       ("measure_stop", 400286)]:
        invalid = {**found, name: {"tick": tick}}
        with pytest.raises(ValueError, match="observation window"):
            marker_bounds(invalid)


def test_ibex_gls_retirement_compares_relative_cycles_and_complete_trace(tmp_path):
    a, b = tmp_path / "rtl", tmp_path / "gls"
    a.write_text("header\n20 6 00100080 00c0006f ignored\n24 8 0010008c 00000093\n")
    b.write_text("header\n21 6 00100080 00c0006f ignored\n25 8 0010008c 00000093\n")
    compare_retirement(a, b, 286, 287)
    b.write_text(b.read_text().replace("25 8", "27 9"))
    with pytest.raises(ValueError, match="retirement differs"):
        compare_retirement(a, b, 286, 287)
    b.write_text("header\n21 6 00100080 00c0006f\n")
    with pytest.raises(ValueError, match="count differs"):
        compare_retirement(a, b, 286, 287)


def test_ibex_gls_config_uses_system_base_isa_not_core_default():
    assert PARAMETERS["BaseIsa"] == "ibex_pkg::BaseIsaRV32IorCHERIoT"
    assert PARAMETERS["RegFile"] == "ibex_pkg::RegFileFF"
    assert PARAMETERS["ICache"] == 0
    assert PARAMETERS["DmBaseAddr"] == "32'h00100000"


def test_ibex_gls_rejects_unknown_closure_configuration(tmp_path):
    vc = tmp_path / "simulation.vc"
    vc.write_text("-DRVFI=1\n-DRV32M=ibex_pkg::RV32MSlow\n")
    with pytest.raises(ValueError, match="unsupported simulation defines"):
        closure(vc)


def test_ibex_gls_adapter_removes_only_dpi_and_mapped_parameters():
    system = 'module system;\nwire a;\n  export "DPI-C" function mhpmcounter_num;\nfunction f; endfunction\nendmodule\n'
    assert system_harness(system) == "module system;\nwire a;\nendmodule\n"
    trace = "ibex_top #( .RV32M (RV32M) ) u_ibex_top (.clk_i);\nibex_tracer tracer();"
    assert tracing_harness(trace).endswith("ibex_top u_ibex_top (.clk_i);\nibex_tracer tracer();")
    assert "always @(negedge clk_i) gls_instr_rdata_i <= instr_rdata_i;" in tracing_harness(trace)
    assert "assign #1 instr_addr_o" not in tracing_harness(trace)
    with pytest.raises(ValueError):
        system_harness("module new_system; endmodule")
    with pytest.raises(ValueError):
        tracing_harness("module new_tracer; endmodule")


def test_ibex_gls_hashes_fail_closed_and_paths_are_not_yosys_code(tmp_path):
    artifact = tmp_path / "mapped.v"
    artifact.write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_hashes({str(artifact): "0" * 64})
    for name in ["space name", "a;delete", 'a"b', "a\nb"]:
        with pytest.raises(ValueError, match="unsupported Yosys path"):
            yosys_path(Path(name))


def test_ibex_gls_reference_does_not_accept_success_flag_alone(tmp_path):
    program = {"registers": [0] * 8, "memory_seed": 1,
               "segments": [{"weight": 1, "release": 0,
                             "body": [{"op": "add", "dst": 0, "a": 0, "b": 1}]}]}
    (tmp_path / "program.json").write_text(json.dumps(program))
    (tmp_path / "functional.json").write_text(json.dumps({"functional_ok": True, "expected": {}}))
    with pytest.raises(ValueError, match="not valid for this program"):
        checked_reference(tmp_path)


def test_ibex_gls_dispatcher_preserves_distinct_marker_bounds(tmp_path, monkeypatch):
    from agcws.designs.ibex import gls

    def fake_replay(synthesis, rtl, out):
        (out / "receipt.json").write_text(json.dumps({
            "rtl_bounds": [286, 400286], "gls_bounds": [288, 400288],
            "clock": "TOP.gls.clk", "rtl_clock": "TOP.rtl.clk", "sta_scope": "gls/dut"}))
        (out / "activity.vcd").write_text("$timescale 1ps $end\n$enddefinitions $end\n#0\n#400288\n")

    def fake_convert(command, stdout, check):
        stdout.write("$timescale 1ps $end\n$enddefinitions $end\n#0\n#400286\n")

    monkeypatch.setattr(gls, "replay", fake_replay)
    monkeypatch.setattr(gls.subprocess, "run", fake_convert)
    result = gls.replay_trial(tmp_path, tmp_path, tmp_path / "replay")
    assert result["bounds"] == [288 * 5000, 400288 * 5000]
    assert result["rtl_bounds"] == [286 * 5000, 400286 * 5000]
    assert result["expected_period_s"] == 1e-8


def test_ibex_gls_reference_clock_exact_scaling_preserves_values(tmp_path):
    from agcws.designs.ibex.gls import reference_clock_vcd
    source, target = tmp_path / "native.vcd", tmp_path / "power.vcd"
    original = "$timescale\n1ps\n$end\n$enddefinitions $end\n#0\n0!\n#1\n1!\n#2\n0!\n"
    source.write_text(original)
    receipt = reference_clock_vcd(source, target, 5000)
    assert source.read_text() == original
    assert target.read_text() == original.replace("#1\n", "#5000\n").replace("#2\n", "#10000\n")
    assert receipt["reference_last_tick"] == 10000
    assert receipt["source_sha256"] != receipt["waveform_sha256"]


def test_counter_configuration_is_explicit_and_bounded():
    from agcws.designs.ibex.gls import effective_parameters
    assert effective_parameters(12)['MHPMCounterNum'] == 12
    assert PARAMETERS['MHPMCounterNum'] == 0
    for value in (-1, 30, True, 12.0):
        with pytest.raises(ValueError):
            effective_parameters(value)
