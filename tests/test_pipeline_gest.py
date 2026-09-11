import copy
import random

import pytest

from agcws.pipeline.ibex.program import canonical, random_program
from agcws.pipeline.policies.gest import Bridge, decode, encode, upstream


def observations(batch, valid=True):
    return [
        {
            **p,
            "valid": valid,
            "loss": 0.2 if valid else None,
            "stage": None if valid else "USEFUL_WORK",
            "reason": None if valid else "below floor",
        }
        for p in batch
    ]


def test_language_roundtrip():
    for seed in range(100):
        program = random_program(random.Random(seed))
        assert decode(encode(program)) == canonical(program)


def test_deterministic_operators_and_parent_isolation():
    bridges = [Bridge(42, 20), Bridge(42, 20)]
    for offset in range(0, 20, 2):
        old = [[decode(p.sequence) for p in b._valid] for b in bridges]
        batches = [b.ask() for b in bridges]
        assert batches[0] == batches[1]
        assert [[decode(p.sequence) for p in b._valid] for b in bridges] == old
        for bridge, batch in zip(bridges, batches, strict=True):
            for p in batch:
                assert canonical(p["program"]) == p["program"]
                assert all(parent <= offset for parent in p["parents"])
                assert p["operator"] == ("bootstrap" if offset == 0 else "gest-uniform+replacement")
            bridge.tell(observations(batch))
    with pytest.raises(RuntimeError, match="exhausted"):
        bridges[0].ask()


def test_rejections_charge_budget_and_no_hidden_retries():
    bridge = Bridge(1, 4)
    for _ in range(2):
        batch = bridge.ask()
        assert all(p["operator"] == "bootstrap" for p in batch)
        bridge.tell(observations(batch, False))
    assert bridge.used == 4 and not bridge._valid


def test_tell_is_atomic_and_cannot_relabel_proposal():
    bridge = Bridge(1, 4)
    batch = bridge.ask()
    with pytest.raises(RuntimeError, match="pending"):
        bridge.ask()
    bad = observations(batch)
    bad[1]["loss"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        bridge.tell(bad)
    assert not bridge._valid
    bad = observations(batch)
    bad[0]["program"] = {}
    with pytest.raises(ValueError, match="match"):
        bridge.tell(bad)
    bridge.tell(observations(batch))
    with pytest.raises(ValueError, match="pending"):
        bridge.tell(observations(batch))


def test_returned_proposal_mutation_does_not_change_pending():
    bridge = Bridge(1, 2)
    batch = bridge.ask()
    original = copy.deepcopy(batch)
    batch[0]["program"]["registers"][0] ^= 1
    bridge.tell(observations(original))


@pytest.mark.parametrize("budget", [0, 1, 3, True, 2.0])
def test_bad_budget(budget):
    with pytest.raises(ValueError, match="even"):
        Bridge(1, budget)


def test_missing_upstream_is_not_a_policy_fallback(tmp_path):
    with pytest.raises(FileNotFoundError):
        upstream(tmp_path)


def test_changed_upstream_is_rejected_before_execution(tmp_path):
    (tmp_path / "Algorithm.py").write_text("raise RuntimeError('must not execute')")
    with pytest.raises(ValueError, match="changed upstream"):
        upstream(tmp_path)


def test_invalid_score_and_missing_batch_are_rejected():
    bridge = Bridge(7, 2)
    batch = bridge.ask()
    with pytest.raises(ValueError, match="exact pending"):
        bridge.tell(observations(batch[:1]))
    invalid = observations(batch, False)
    invalid[0]["loss"] = 0.0
    with pytest.raises(ValueError, match="no score"):
        bridge.tell(invalid)
    assert bridge.used == 2 and not bridge._valid
