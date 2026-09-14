import runpy

import pytest


def test_late_feedback_requires_real_terminal_generation_not_initialization():
    eligible = runpy.run_path("analysis/late_feedback.py")["eligible"]
    history = [{"slot": i, "valid": i <= 2} for i in range(1, 17)]
    assert not eligible(history)
    history[-1]["valid"] = True
    assert eligible(history)
    history[5]["valid"] = True
    assert not eligible(history)
    with pytest.raises(ValueError, match="sixteen"):
        eligible(history[:-1])
