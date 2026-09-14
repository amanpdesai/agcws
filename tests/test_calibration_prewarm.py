import runpy

import pytest

from agcws.pipeline.backends import backend
from agcws.pipeline.policies.dispatch import Policy


def test_premeasurement_matches_charged_policy(tmp_path):
    cases = runpy.run_path("scripts/prewarm_random_calibration.py")["cases"]
    spec = {"domain": "redmule-temporal-long", "policies": ["random"],
            "stop_on_success": False, "targets": {"calibration_only": [0.0]*8},
            "budget": 32, "seeds": [7200, 7201], "batch_size": 2}
    expected = cases(spec, backend(spec["domain"]))
    actual = []
    for seed in spec["seeds"]:
        policy = Policy("random", seed, spec, [0.0]*8, {}, None)
        history = []
        while len(history) < 32:
            batch = policy.propose(history, tmp_path, {})
            actual.extend({"seed": seed, "slot": p["slot"], "program": p["program"]} for p in batch)
            history.extend(batch)
    assert actual == expected
    with pytest.raises(ValueError):
        cases({**spec, "policies": ["phase-ga"]}, backend(spec["domain"]))
