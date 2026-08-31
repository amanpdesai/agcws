import json

from scripts.aggregate_axi_dma_calibration import main


def test_aggregate_axi_dma_calibration(tmp_path, monkeypatch):
    root = tmp_path / "run"
    (root / "workloads").mkdir(parents=True)
    workload = {"transfers": [{"src": 0, "dst": 32768, "length": 4096}]}
    (root / "workloads" / "workload-00001.json").write_text(json.dumps(workload))
    trial = {"trial_id": "random-00000", "validity": {"valid": True},
             "profile": {"mean_power": 3.5, "fidelity": "activity"}}
    (root / "trials.jsonl").write_text(json.dumps(trial) + "\n")
    out = tmp_path / "calibration.json"
    monkeypatch.setattr("sys.argv", ["aggregate", str(root), "--out", str(out)])
    main()
    result = json.loads(out.read_text())
    assert result["p_min"] == result["p_max"] == 3.5
    assert len(result["records"]) == 1
