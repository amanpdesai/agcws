"""Opt-in CPU integration; retains every artifact under AGCWS_MESH_INTEGRATION_OUT."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from agcws.designs.mesh import gls, simulate
from agcws.designs.mesh.adapter import MeshTemporalAdapter


@pytest.mark.skipif(not os.environ.get("AGCWS_MESH_INTEGRATION_OUT"),
                    reason="set a fresh AGCWS_MESH_INTEGRATION_OUT to run EDA tools")
def test_real_mapped_mesh_replay():
    root = Path(os.environ["AGCWS_MESH_INTEGRATION_OUT"]).resolve()
    root.mkdir(parents=True, exist_ok=False)
    phases = json.loads(Path("tests/unit/mesh_matched_workload.json").read_text())
    workload = MeshTemporalAdapter().elaborate(phases)
    gls.write_json(root / "workload.json", workload)
    synthesis = Path(os.environ.get("AGCWS_MESH_SYNTHESIS", root / "synthesis")).resolve()
    if not os.environ.get("AGCWS_MESH_SYNTHESIS"):
        gls.main(["synthesize", "--out", str(synthesis)])
    simulate.main([str(root / "workload.json"), "--out", str(root / "rtl"), "--jobs", "2"])
    gls.write_json(root / "rtl/workload.json", workload)
    prepared = gls.replay_trial(root / "rtl", synthesis, root / "gls")
    assert prepared["clock"] == "clk_i" and prepared["scope"] == "mesh_temporal/dut"
    rtl = json.loads((root / "rtl/functional.json").read_text())
    mapped = json.loads((root / "gls/functional.json").read_text())
    assert rtl == mapped and mapped["received"] == 256
    receipt = json.loads((root / "gls/provenance.json").read_text())
    assert receipt["matched_grid"]["clock_edges"] == 8200
    assert receipt["matched_grid"]["edge_indices"] == list(range(0, 8201, 1025))
    # A real mapped failure, with the same 64-packet floor, must not emit success.
    late = {"packets": [{"release_cycle": 8191, "source": i % 4,
                          "destination": 3 - i % 4, "payload": i} for i in range(64)],
            "sink_period": 8, "sink_pause": 3}
    negative = root / "negative"
    negative.mkdir()
    (negative / "program.txt").write_text(simulate.packet_program(late))
    binary = gls.config.ROOT / "out/.cache/mesh-matched-gls" / receipt["build_key"] / "simulate"
    with pytest.raises(subprocess.CalledProcessError):
        gls.run([binary, f"+PROGRAM={negative / 'program.txt'}", "+SINK_PERIOD=8", "+SINK_PAUSE=3"],
                negative / "run.log", cwd=negative)
    assert "MESH_INCOMPLETE" in (negative / "run.log").read_text()
    assert not (negative / "functional.json").exists()
