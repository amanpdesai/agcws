from agcws.analysis.aggregate import aggregate_summaries


def test_aggregate_keeps_unsolved_runs_in_denominator():
    result = aggregate_summaries([
        {"policy": "random", "design": "aes", "solved": True,
         "auc_best_so_far": 1.0, "evaluations_to_target": 4},
        {"policy": "random", "design": "aes", "solved": False,
         "auc_best_so_far": 2.0, "evaluations_to_target": 8},
    ])
    assert result == [{
        "policy": "random", "design": "aes", "runs": 2,
        "solve_rate": 0.5, "mean_auc_best_so_far": 1.5,
        "mean_evaluations_to_target": 6.0,
    }]
