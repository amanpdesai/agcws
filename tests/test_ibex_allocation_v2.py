import random

import pytest

from experiments.ibex_temporal_v1 import program as v1
from experiments.ibex_temporal_v2 import program as v2
from experiments.ibex_temporal_v2.compiler import assembly


def test_allocation_exact_positive_deterministic():
    rng = random.Random(23)
    for _ in range(2000):
        weights = [rng.randint(1, 4096) for _ in range(rng.randint(1, 8))]
        allocation = v2.allocate(weights)
        assert sum(allocation) == 4096 and min(allocation) > 0
        assert allocation == v2.allocate(weights)
    assert v2.allocate([1] * 8) == [512] * 8
    assert v2.allocate([4096, 1, 1, 1, 1, 1, 1, 1]) == [4089, 1, 1, 1, 1, 1, 1, 1]


@pytest.mark.parametrize("weights", [[], [True], [0], [-1], [4097], [1] * 9, [1.0]])
def test_bad_weights_rejected_not_repaired(weights):
    with pytest.raises(ValueError):
        v2.allocate(weights)


def test_v1_embedding_preserves_full_architectural_state():
    rng = random.Random(123)
    for _ in range(30):
        old = v1.random_program(rng)
        new = v2.from_v1(old)
        expected, observed = v1.interpret(old), v2.interpret(new)
        assert all(observed[k] == expected[k] for k in expected)
        assert assembly(new) == v1.assembly(old)


def test_partial_iteration_has_defined_prefix_effects():
    program = {
        "registers": [0, 1, 0, 0, 0, 0, 0, 0],
        "memory_seed": 0,
        "segments": [
            {
                "weight": 1,
                "release": 0,
                "body": [
                    {"op": "add", "dst": 0, "a": 0, "b": 1},
                    {"op": "add", "dst": 2, "a": 2, "b": 1},
                    {"op": "add", "dst": 3, "a": 3, "b": 1},
                ],
            }
        ],
    }
    result = v2.interpret(program)
    assert result["registers"][:4] == [1366, 1, 1365, 1365]
    assert result["useful_work"] == 4096
    code = assembly(program)
    assert "  li t6, 1365" in code
    assert code.count("  add a0, a0, a1") == 2


def test_mutations_conserve_work():
    rng = random.Random(56)
    program = v2.random_program(rng)
    for _ in range(100):
        program = v2.mutate(program, rng)
        assert sum(v2.allocation(program)) == 4096
