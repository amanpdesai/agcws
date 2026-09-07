import json
import random

from experiments.ibex_temporal_v2.program import allocation, random_program
from experiments.ibex_temporal_v2.search import PROMPT, ProgramAgent


def test_feedback_retains_allocation_and_signed_window_residuals():
    program = random_program(random.Random(600))
    trial = {
        "slot": 1,
        "program": program,
        "valid": True,
        "reason": "",
        "loss": 0.2,
        "rates": list(range(8)),
        "residual": [-0.2] * 4 + [0.2] * 4,
        "allocation": allocation(program),
        "tokens_in": 123,
    }
    payload = json.loads(ProgramAgent.build_payload(None, {}, [trial], 2, PROMPT))
    assert payload["history"][0]["allocation"] == allocation(program)
    assert sum(payload["history"][0]["allocation"]) == 4096
    assert payload["history"][0]["residual"] == trial["residual"]
    assert "tokens_in" not in payload["history"][0]
    assert payload["batch_size"] == 2
    assert "weight" in json.dumps(payload["schema"])
    assert "iterations" not in json.dumps(payload["schema"])
