import copy
import random

import numpy as np
import pytest

from agcws.baselines.temporal_model import features, propose, timing_edit
from agcws.designs.temporal_registry import backend
from agcws.designs.workloads.schedule import expand_schedule

DOMAINS = ("aes-temporal", "dma-temporal", "ibex-temporal", "mesh-temporal", "redmule-temporal-long")


@pytest.mark.parametrize("domain", DOMAINS)
def test_determinism_parent_visibility_and_no_measurements(domain, monkeypatch):
    design = backend(domain)

    def forbidden(*args, **kwargs):
        raise AssertionError("policy may not measure candidates")

    monkeypatch.setattr(design, "measured", forbidden)

    def trajectory():
        rng, history, decisions = random.Random(731), [], []
        for slot in range(1, 25):
            before = copy.deepcopy(history)
            program, parents, note = propose(design, rng, slot, history)
            assert history == before
            assert all(parent < slot for parent in parents)
            assert note["extra_simulations"] == 0
            assert note["training_slots"] == list(range(1, slot))
            vector = features(program, design)
            assert len(vector) == 33 and np.isfinite(vector).all()
            residual = vector[1:9].tolist()  # Synthetic fixture, not empirical evidence.
            history.append({"slot": slot, "program": program, "canonical_program": program,
                            "valid": True, "loss": float(np.linalg.norm(residual)), "residual": residual})
            decisions.append(note)
        return history, decisions

    left = trajectory()
    assert left == trajectory()
    assert any(n["mode"] == "ridge-timing-refinement" for n in left[1])


@pytest.mark.parametrize("domain", ("aes-temporal", "dma-temporal"))
def test_timing_edits_preserve_exact_resources(domain):
    design, rng = backend(domain), random.Random(37)
    program = design.random(rng)
    for _ in range(100):
        program = timing_edit(program, design, rng)
        expand_schedule(program, design.contract)


def test_nonfinite_measurement_is_not_silently_replaced():
    design = backend("aes-temporal")
    with pytest.raises(ValueError, match="finite"):
        propose(design, random.Random(1), 2, [{"slot": 1, "valid": True, "residual": [float("nan")] * 8}])
