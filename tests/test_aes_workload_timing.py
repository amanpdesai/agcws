from scripts.run_aes_workload import idle_pattern


def test_idle_operations_preserve_interblock_schedule():
    workload = {
        "operations": [
            {"op": "configure"},
            {"op": "encrypt", "blocks": 2},
            {"op": "idle", "cycles": 7},
            {"op": "encrypt", "blocks": 2},
            {"op": "idle", "cycles": 3},
            {"op": "encrypt", "blocks": 1},
        ]
    }
    assert idle_pattern(workload, 5) == "0,0,7,0"
