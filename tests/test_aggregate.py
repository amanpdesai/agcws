import json

from agcws.analysis.aggregate import aggregate_summaries
from scripts.aggregate_runs import main


def test_aggregate_reports_cost_and_validity_metrics():
    result = aggregate_summaries([{
        "policy": "agent", "design": "aes", "target": "0.5",
        "solved": True, "auc_best_so_far": 1.0, "evaluations_to_target": 3,
        "valid_trials": 2, "simulations": 2, "tokens_in": 10,
        "tokens_out": 4, "validity_failures": {"SCHEMA": 1},
    }])[0]
    assert result["tokens_in"] == 10
    assert result["validity_failures"]["SCHEMA"] == 1


def test_aggregate_keeps_unsolved_runs_in_denominator():
    result = aggregate_summaries([
        {"policy": "random", "design": "aes", "solved": True,
         "target": "0.5", "auc_best_so_far": 1.0, "evaluations_to_target": 4},
        {"policy": "random", "design": "aes", "solved": False,
         "target": "0.5", "auc_best_so_far": 2.0, "evaluations_to_target": 8},
    ])
    assert result == [{
        "policy": "random", "design": "aes", "runs": 2,
        "target": "0.5",
        "solve_rate": 0.5, "mean_auc_best_so_far": 1.5,
        "mean_evaluations_to_target": 6.0,
        "auc_best_so_far_ci95": {"mean": 1.5, "lower": 1.0, "upper": 2.0},
        "evaluations_to_target_ci95": {"mean": 6.0, "lower": 4.0, "upper": 8.0},
        "valid_trials": 0, "simulations": 0, "tokens_in": 0, "tokens_out": 0,
        "validity_failures": {"SCHEMA": 0, "PROTOCOL": 0,
                              "FUNCTIONAL": 0, "USEFUL_WORK": 0},
    }]


def test_aggregate_keeps_profile_targets_separate():
    base = {"policy": "random", "design": "aes", "target": "profile",
            "solved": False, "auc_best_so_far": 1.0,
            "evaluations_to_target": 2}
    result = aggregate_summaries([base | {"target_source": "burst"},
                                  base | {"target_source": "ramp"}])
    assert [row["target_source"] for row in result] == ["burst", "ramp"]


def test_aggregate_runs_recovers_target_identity_from_archived_target_file(
        tmp_path, monkeypatch, capsys):
    run = tmp_path / "run"
    run.mkdir()
    (run / "summary.json").write_text(json.dumps({
        "policy": "random", "design": "aes", "target": "profile",
        "solved": False, "auc_best_so_far": 1.0,
        "evaluations_to_target": 2,
    }))
    (run / "target.json").write_text(json.dumps({"source": "burst"}))
    monkeypatch.setattr("sys.argv", ["aggregate_runs.py", str(tmp_path)])
    main()
    result = json.loads(capsys.readouterr().out)
    assert result[0]["target_source"] == "burst"
