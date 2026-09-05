from scripts.check_transaction_temporal_shapes import schedules


def test_temporal_schedules_match_work_and_idle_budgets():
    cases = schedules()
    assert len(cases) == 5
    for operations in cases.values():
        assert sum(op.get('blocks', 0) for op in operations) == 64
        assert sum(op.get('cycles', 0) for op in operations) == 6000
