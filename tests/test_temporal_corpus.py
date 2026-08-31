from scripts.run_aes_temporal_corpus import schedule_workload
from agcws.policies.temporal_search import TemporalRandomSearch


def test_temporal_schedule_has_explicit_idle_operations():
    workload = schedule_workload("low_high_low", 8)
    assert sum(op.get("blocks", 0) for op in workload["operations"] if op["op"] == "encrypt") == 8
    assert [op["cycles"] for op in workload["operations"] if op["op"] == "idle"] == [80, 80, 80]


def test_burst_schedule_has_no_idle_gaps():
    workload = schedule_workload("burst", 4)
    assert all(op["op"] != "idle" for op in workload["operations"])


def test_temporal_policy_is_seed_reproducible():
    first = TemporalRandomSearch(4).propose(None, None, [], 2)
    second = TemporalRandomSearch(4).propose(None, None, [], 2)
    assert first == second


def test_temporal_policy_default_clears_aes_useful_work_floor():
    workload = TemporalRandomSearch(4).propose(None, None, [], 1)[0]
    assert sum(op.get("blocks", 0) for op in workload["operations"] if op["op"] == "encrypt") >= 38


def test_temporal_corpus_requires_cached_evaluation_outputs():
    from pathlib import Path
    text = Path("scripts/run_aes_temporal_corpus.py").read_text()
    assert 'required_outputs=("result.json", "activity.json")' in text


def test_temporal_corpus_ramp_respects_idle_cap():
    workload = schedule_workload("ramp", 48)
    assert sum(op.get("cycles", 0) for op in workload["operations"]) <= 10000
