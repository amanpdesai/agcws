import json
from pathlib import Path

from scripts.validate_finalists import select_finalists


def test_select_finalists_orders_valid_trials_and_excludes_invalid(tmp_path: Path):
    path = tmp_path / "trials.jsonl"
    rows = [
        {"trial_id": "bad", "loss": 0.01,
         "validity": {"valid": False}, "workload": {}},
        {"trial_id": "second", "loss": 0.2,
         "validity": {"valid": True}, "workload": {"x": 2}},
        {"trial_id": "first", "loss": 0.1,
         "validity": {"valid": True}, "workload": {"x": 1}},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    selected = select_finalists(path, 2)
    assert [row["trial_id"] for row in selected] == ["first", "second"]
