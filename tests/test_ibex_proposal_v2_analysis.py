import json

import pytest

from analysis.ibex_proposal_v2 import readiness


def write_panel(root, stages):
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "targets": {"t": {}},
                "seeds": [600],
                "budget": len(stages) + 2,
                "shared_initial_slots": 2,
                "readiness": {
                    "model_valid_fraction_min": 0.8,
                    "work_count_rejections_max": 0,
                    "functional_failures_max": 0,
                },
            }
        )
    )
    path = root / "panel/t/seed-600/agent"
    path.mkdir(parents=True)
    rows = [
        {
            "slot": i + 1,
            "valid": stage == "VALID",
            "stage": None if stage == "VALID" else stage,
            "reason": "test",
        }
        for i, stage in enumerate(["VALID", "VALID", *stages])
    ]
    (path / "trials.jsonl").write_text("\n".join(json.dumps(row) for row in rows))


def test_readiness_excludes_shared_initialization(tmp_path):
    write_panel(tmp_path, ["VALID"] * 3 + ["SCHEMA"] * 2)
    report = readiness(tmp_path)
    assert report["model_generated_slots"] == 5
    assert report["model_generated_valid_fraction"] == 0.6
    assert not report["ready"]


def test_exact_threshold_passes_but_architectural_failure_does_not(tmp_path):
    write_panel(tmp_path, ["VALID"] * 4 + ["SCHEMA"])
    assert readiness(tmp_path)["ready"]
    path = tmp_path / "panel/t/seed-600/agent/trials.jsonl"
    path.write_text(path.read_text().replace("SCHEMA", "FUNCTIONAL"))
    assert not readiness(tmp_path)["ready"]


def test_incomplete_model_panel_cannot_pass(tmp_path):
    write_panel(tmp_path, ["VALID"] * 5)
    path = tmp_path / "panel/t/seed-600/agent/trials.jsonl"
    path.write_text("\n".join(path.read_text().splitlines()[:-1]))
    with pytest.raises(ValueError, match="incomplete"):
        readiness(tmp_path)
