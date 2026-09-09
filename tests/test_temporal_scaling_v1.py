import copy
import random

import pytest

from experiments.ibex_temporal_v3.program import allocation, canonical
from experiments.temporal_scaling_v1.baselines import mutate, phase_ga, phase_random
from experiments.temporal_scaling_v1.smoke import propose
from experiments.temporal_scaling_v1.targets import (
    Request,
    generate,
    match_request,
    witnessed_target,
)


def test_request_duration_changes_time_not_shape():
    a = generate(Request(seed=3))
    b = generate(Request(seed=3, horizon_cycles=400000))
    assert a["target_rates"] == b["target_rates"]
    assert a["id"] != b["id"]
    assert b["bin_edges_cycles"] == [2 * v for v in a["bin_edges_cycles"]]
    assert a == generate(Request(seed=3))
    assert a["status"] == "unqualified-request"
    assert a["observed_shape"]["transitions"] == 3


@pytest.mark.parametrize(
    "kwargs",
    [
        {"bins": 0},
        {"bins": True},
        {"horizon_cycles": 9},
        {"phases": 9},
        {"phases": 1},
        {"low": float("nan")},
        {"scale": 0},
        {"family": "unknown"},
        {"seed": -1},
        {"low": 0.9, "high": 0.1},
    ],
)
def test_request_rejects_invalid_specs(kwargs):
    with pytest.raises(ValueError):
        generate(Request(seed=kwargs.pop("seed", 3), **kwargs))


@pytest.mark.parametrize(
    "family", ["ramp", "flat", "burst", "alternating", "random_steps"]
)
def test_request_families(family):
    request = generate(Request(seed=77, family=family, bins=32))
    assert len(request["target_rates"]) == 32
    assert all(0.2 <= x <= 0.8 for x in request["normalized_rates"])
    assert request["bin_edges_cycles"][-1] == 200000


def test_witness_requires_valid_matching_window_and_arithmetic():
    program = phase_random(random.Random(1), 1)
    result = {
        "valid": True,
        "cache_id": "test",
        "profile": {
            "clock_edges": 200000,
            "window_rates": [2.0] * 8,
            "window_bit_transitions": [50000] * 8,
        },
    }
    target = witnessed_target(program, result, "fingerprint", 4.0)
    request = generate(Request(seed=1, family="flat", scale=4.0))
    assert match_request(request, target, 0.0)["qualified"]
    altered = copy.deepcopy(result)
    altered["profile"]["clock_edges"] = 400000
    with pytest.raises(ValueError):
        witnessed_target(program, altered, "fingerprint", 4.0)
    altered = copy.deepcopy(result)
    altered["profile"]["window_rates"][0] = 1.0
    with pytest.raises(ValueError):
        witnessed_target(program, altered, "fingerprint", 4.0)
    with pytest.raises(ValueError):
        witnessed_target(program, {**result, "valid": False}, "fingerprint", 4.0)
    with pytest.raises(ValueError):
        match_request(generate(Request(seed=1, bins=16)), target, 0.1)
    other = generate(Request(seed=1, family="flat", low=0.8, high=1.0, scale=4.0))
    assert not match_request(other, target, 0.1)["qualified"]


def test_phase_controls_are_legal_deterministic_and_structural():
    history = []
    rng = random.Random(13)
    for slot in range(1, 81):
        program = phase_random(rng, slot)
        assert len(program["segments"]) == 1 + (slot - 1) % 8
        assert sum(allocation(program)) == 4096
        altered, _ = mutate(program, rng)
        assert canonical(altered) == altered
        history.append(
            {
                "slot": slot,
                "valid": True,
                "loss": 1 / slot,
                "canonical_program": program,
            }
        )
    for seed in range(30):
        candidate, provenance = phase_ga(random.Random(seed), 81, history)
        assert candidate == phase_ga(random.Random(seed), 81, history)[0]
        assert sum(allocation(candidate)) == 4096
        assert provenance["operator"].startswith("crossover+")
        assert all(i <= 80 for i in provenance["parents"])


def test_bootstrap_and_immigration_are_explicit_and_bad_dispatch_raises():
    candidate, reason = phase_ga(random.Random(1), 1, [])
    assert reason == {"operator": "bootstrap", "parents": []}
    with pytest.raises(ValueError):
        propose("typo", random.Random(1), 3, [])
    with pytest.raises(ValueError):
        phase_ga(random.Random(1), 1, [{"slot": 1, "valid": False}])
    assert canonical(candidate) == candidate


def test_shared_initial_programs_are_identical_across_arms():
    batches = []
    for arm in ("legacy-random", "phase-random", "phase-ga"):
        rng = random.Random(830)
        batches.append([propose(arm, rng, slot, [])[0] for slot in (1, 2)])
    assert batches[0] == batches[1] == batches[2]


def test_every_mutation_operator_is_exercised():
    rng = random.Random(91)
    program = phase_random(rng, 4)
    observed = {mutate(program, rng)[1] for _ in range(128)}
    assert observed == {
        "release",
        "weight",
        "instruction",
        "register",
        "swap",
        "mix",
        "insert",
        "delete",
    }
