from pathlib import Path


def test_baseline_matrix_uses_common_activity_runner():
    text = Path("scripts/run_aes_baseline_matrix.sh").read_text()
    for policy in ("random", "mutation", "evolutionary", "offline-hybrid"):
        assert policy in text
    assert "--fidelity activity" in text
    assert 'target=${AGCWS_SEARCH_TARGET:-0.5}' in text
    assert 'epsilon=${AGCWS_SEARCH_EPSILON:-0.05}' in text
    assert 'targets=${AGCWS_SEARCH_TARGETS:-$target}' in text
    assert "AGCWS_SEARCH_POLICIES" in text
    assert 'resume=${AGCWS_RESUME:-0}' in text
    assert 'completed=$(wc -l < "$run_dir/trials.jsonl")' in text
    assert '"$completed" -eq "$budget"' in text
    assert "aggregate_runs.py" in text
