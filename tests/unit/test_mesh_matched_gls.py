import json
from pathlib import Path

import pytest

from agcws.designs.mesh import gls


def test_mapped_harness_reuses_driver_and_guards_only_dut():
    source = Path("src/agcws/designs/mesh/assets/mesh_temporal.sv").read_text()
    dut, driver = source.split("`ifndef SYNTHESIS")
    assert dut.startswith("`ifndef AGCWS_MESH_MAPPED")
    assert "module agcws_mesh" in dut and dut.rstrip().endswith("`endif")
    assert "module mesh_temporal" in driver
    assert "MESH_FUNCTIONAL_MISMATCH" in driver and "MESH_INCOMPLETE" in driver
    assert "repeat (8)" in driver and "cycle < 8192" in driver


@pytest.mark.parametrize("log", ["", "AGCWS_MESH_DONE sent=63 received=64 cycles=8200",
    "AGCWS_MESH_DONE sent=64 received=64 cycles=8192",
    "MESH_FUNCTIONAL_MISMATCH\nAGCWS_MESH_DONE sent=64 received=64 cycles=8200",
    "MESH_INCOMPLETE\nAGCWS_MESH_DONE sent=64 received=64 cycles=8200"])
def test_completion_fails_closed(log):
    with pytest.raises(ValueError, match="completion"):
        gls.check_completion(log, 64)


def test_completion_checked():
    result = gls.check_completion("AGCWS_MESH_DONE sent=64 received=64 cycles=8200", 64)
    assert result["valid"] and result["useful_packets"] == 64


def test_synthesis_rejects_modified_netlist_and_sources(tmp_path, monkeypatch):
    liberty, rtl, netlist = (tmp_path / name for name in ("cells.lib", "dut.sv", "mapped.v"))
    for path in (liberty, rtl, netlist):
        path.write_text(path.name)
    monkeypatch.setattr(gls.config, "LIBERTY", liberty)
    manifest = {"top": gls.TOP, "netlist_sha256": gls.sha(netlist),
                "liberty_sha256": gls.sha(liberty), "sources": {str(rtl): gls.sha(rtl)}}
    gls.write_json(tmp_path / "manifest.json", manifest)
    assert gls.validate_synthesis(tmp_path) == manifest
    rtl.write_text("changed")
    with pytest.raises(ValueError, match="source changed"):
        gls.validate_synthesis(tmp_path)
    netlist.write_text("changed")
    with pytest.raises(ValueError, match="netlist/top/Liberty"):
        gls.validate_synthesis(tmp_path)


def test_rtl_receipt_requires_matched_pacing_program_and_identity(tmp_path):
    waveform = tmp_path / "activity.vcd"
    waveform.write_text("waveform")
    program = "0 0 3 00000000\n"
    (tmp_path / "program.txt").write_text(program)
    gls.write_json(tmp_path / "functional.json", {"valid": True, "sent": 64, "received": 64})
    workload = {"packets": [{}] * 64, "sink_period": 8, "sink_pause": 3}
    harness = Path("src/agcws/designs/mesh/assets/mesh_temporal.sv").resolve()
    manifest = {"sources": {str(harness): gls.sha(harness)}}
    provenance = {"observation_cycles": 8200, "reset_cycles": 8, "scope": "mesh_temporal.dut",
                  "sink_period": 8, "sink_pause": 3,
                  "sources_sha256": {"package/mesh/mesh_temporal.sv": gls.sha(harness)}}
    gls.write_json(tmp_path / "provenance.json", provenance)
    assert len(gls.validate_rtl(waveform, program, workload, manifest)) == 4
    with pytest.raises(ValueError, match="programs differ"):
        gls.validate_rtl(waveform, "different", workload, manifest)
    workload["sink_pause"] = 0
    with pytest.raises(ValueError, match="pacing"):
        gls.validate_rtl(waveform, program, workload, manifest)
    workload["sink_pause"] = 3
    provenance["sources_sha256"]["package/mesh/mesh_temporal.sv"] = "frozen-other-source"
    gls.write_json(tmp_path / "provenance.json", provenance)
    with pytest.raises(ValueError, match="source identity"):
        gls.validate_rtl(waveform, program, workload, manifest)


def test_cli_preserves_failure_and_refuses_overwrite(tmp_path, monkeypatch):
    def fail(out):
        (out / "synthesis.log").write_text("original failure")
        raise RuntimeError("failed synthesis")
    monkeypatch.setattr(gls, "synthesize", fail)
    out = tmp_path / "attempt"
    with pytest.raises(RuntimeError):
        gls.main(["synthesize", "--out", str(out)])
    assert json.loads((out / "failure.json").read_text())["error"] == "failed synthesis"
    with pytest.raises(FileExistsError):
        gls.main(["synthesize", "--out", str(out)])
    assert (out / "synthesis.log").read_text() == "original failure"


def test_shared_dispatcher_contract(tmp_path, monkeypatch):
    rtl, synthesis, out = (tmp_path / name for name in ("rtl", "synthesis", "gls"))
    rtl.mkdir()
    synthesis.mkdir()
    calls = []
    monkeypatch.setattr(gls, "replay", lambda *args: calls.append(args))
    result = gls.replay_trial(rtl, synthesis, out)
    assert calls == [(synthesis, rtl / "workload.json", rtl / "activity.vcd", out)]
    assert result == {"waveform": out / "activity.vcd", "rtl_waveform": rtl / "activity.vcd",
                      "clock": "clk_i", "rtl_clock": "clk_i", "scope": "mesh_temporal/dut",
                      "clock_edges": 8200, "bounds": None, "expected_period_s": 1e-8}
