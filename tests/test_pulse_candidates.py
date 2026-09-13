import runpy

import numpy as np
import pytest

from agcws.adapters.redmule import RedmuleTemporalAdapter

module = runpy.run_path("analysis/pulse_candidates.py")


def test_basis_matches_shifted_pulse_integration():
    samples = np.full(65536, 2.0)
    samples[2048:4096] = 10
    positions, values, duration = module["basis"](samples, 4096)
    assert duration == 2048 and positions[0] == 2048
    assert values[0].tolist() == [2, 0, 0, 0, 0, 0, 0, 0]
    assert np.allclose(values.sum(axis=1), 2)


def test_proposals_are_legal_deterministic_and_never_qualify_from_prediction():
    samples = np.full(65536, 2.0)
    samples[2048:4096] = 10
    args = ([4, 2, 2, 2, 2, 2, 2, 2], samples, 4096)
    candidates = module["propose"](*args, pattern="random", seed=1)
    assert candidates == module["propose"](*args, pattern="random", seed=1)
    assert len(candidates) == 8 and candidates[0]["predicted_mse"] == 0
    for candidate in candidates:
        assert candidate["qualified"] is False
        releases = RedmuleTemporalAdapter().elaborate(candidate["program"])
        assert all(b-a >= 2048 for a, b in zip(releases, releases[1:]))


def test_bad_window_cannot_be_used_as_pulse():
    with pytest.raises(ValueError, match="fixed-window"):
        module["basis"]([0]*10, 9)
