import pytest

from analysis.plot_activity import summarize


def test_summarize_preserves_cycle_and_window_metrics():
    summary = summarize({
        "clock_edges": 4,
        "total_transitions": 10,
        "per_cycle_toggles": [1, 2, 3, 4],
        "window_toggles": [3, 7],
    })

    assert summary == {
        "clock_edges": 4,
        "total_transitions": 10,
        "per_cycle_mean": 2.5,
        "per_cycle_peak": 4,
        "window_count": 2,
        "window_toggles": [3, 7],
        "window_normalized": [3 / 7, 1.0],
    }


def test_summarize_rejects_missing_cycle_activity():
    with pytest.raises(ValueError, match="no per_cycle_toggles"):
        summarize({"window_toggles": [1]})
