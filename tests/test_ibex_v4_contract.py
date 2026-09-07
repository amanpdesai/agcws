import copy
import json
import random

import jsonschema
import pytest

from experiments.ibex_temporal_v3.program import random_program
from experiments.ibex_temporal_v4.contract import decode, response_schema


def program():
    return random_program(random.Random(3))


def test_contract_schema_does_not_mutate_program_schema():
    jsonschema.Draft202012Validator.check_schema(response_schema(2, True))
    a = response_schema(2)
    a["properties"]["candidates"]["items"]["required"].clear()
    assert response_schema(2)["properties"]["candidates"]["items"]["required"]
    with pytest.raises(ValueError):
        response_schema(True)


def test_short_batch_keeps_positions_and_missing_slot_is_charged():
    result = decode(json.dumps({"hypothesis": "test", "candidates": [program()]}), 2)
    assert len(result["slots"]) == 2
    assert result["slots"][0]["canonical"] == program()
    assert result["slots"][1]["program_error"] == "missing requested candidate"
    assert result["response_error"]


def test_nested_envelope_is_never_repaired():
    result = decode(
        json.dumps(
            {
                "hypothesis": "test",
                "candidates": [
                    {"program": program(), "reference_slot": 2},
                    program(),
                ],
            }
        ),
        2,
    )
    assert result["slots"][0]["program_error"]
    assert result["slots"][0]["canonical"] is None
    assert result["slots"][1]["canonical"] == program()


@pytest.mark.parametrize("text", ['{"candidates":[', "null", '{"candidates":[NaN]}'])
def test_bad_json_keeps_requested_slot_count(text):
    result = decode(text, 2)
    assert result["response_error"] and len(result["slots"]) == 2
    assert all(t["canonical"] is None for t in result["slots"])


def test_numeric_equivalence_and_independent_prediction_validation():
    value = json.loads(json.dumps(program()), parse_int=float)
    result = decode(
        json.dumps(
            {
                "hypothesis": "test",
                "candidates": [value],
                "predictions": [{"reference_slot": 1}],
            }
        ),
        1,
        True,
    )
    assert result["slots"][0]["canonical"] == program()
    assert result["slots"][0]["prediction_error"]
    assert result["slots"][0]["program_error"] is None


def test_complete_prediction_contract_and_excess_batch():
    data = {
        "hypothesis": "test",
        "candidates": [program()],
        "predictions": [
            {
                "reference_slot": 2,
                "changed_factor": "divisor",
                "window_directions": [-1] * 8,
            }
        ],
    }
    assert decode(json.dumps(data), 1, True)["response_error"] is None
    changed = copy.deepcopy(data)
    changed["candidates"].append(program())
    assert decode(json.dumps(changed), 1, True)["slots"][0]["canonical"] is None
