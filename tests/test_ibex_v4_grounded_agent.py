import json
import random

from experiments.ibex_temporal_v3.program import random_program, allocation
from experiments.ibex_temporal_v4.grounded_agent import payload


def test_grounding_isolated_from_common_contract_and_preserves_failed_predictions():
    program = random_program(random.Random(600))
    first = {
        "slot": 1,
        "program": program,
        "canonical_program": program,
        "valid": True,
        "reason": "",
        "loss": 0.2,
        "rates": [100] * 8,
        "residual": [0.1] * 8,
        "allocation": allocation(program),
        "proposal_mode": "initial",
    }
    second = {
        **first,
        "slot": 3,
        "rates": [110] * 8,
        "proposal_mode": "agent",
        "prediction": {
            "reference_slot": 1,
            "changed_factor": "test",
            "window_directions": [-1] * 8,
        },
        "execution": {"measured_operand_events": "test"},
    }
    history = [first, second]
    goal = {"profile": [90] * 8, "scale": 100, "tolerance": 0.1}
    base, grounded = [
        json.loads(payload(history, goal, 2, flag)) for flag in (False, True)
    ]
    assert base["response_contract"] == grounded["response_contract"]
    assert base["semantics"] == grounded["semantics"]
    assert "experiment_notebook" not in base
    assert grounded["experiment_notebook"][0]["matched_bins"] == 0
    assert grounded["history"][0]["execution"] is None
    assert grounded["history"][1]["execution"] == second["execution"]
    assert 'Return strict JSON {"hypothesis"' not in grounded["system_prompt"]
