import json
import random

import jsonschema

from agcws.pipeline.ibex.contract import decode
from agcws.pipeline.ibex.native_schema import serving_schema
from agcws.pipeline.ibex.program import random_program


def test_serving_schema_accepts_legal_programs_without_changing_local_acceptance():
    schema = serving_schema(2)
    jsonschema.Draft202012Validator.check_schema(schema)
    for seed in range(20):
        data = {
            "hypothesis": "test",
            "candidates": [random_program(random.Random(seed))],
        }
        jsonschema.validate(data, schema)
        assert decode(json.dumps(data), 2)["slots"][0]["canonical"] is not None
    data["candidates"][0]["registers"] = [0]
    jsonschema.validate(data, schema)
    assert decode(json.dumps(data), 2)["slots"][0]["canonical"] is None


def test_serving_schema_still_rejects_nested_program_envelope():
    value = {
        "hypothesis": "test",
        "candidates": [{"program": random_program(random.Random(3))}],
    }
    assert not jsonschema.Draft202012Validator(serving_schema(2)).is_valid(value)
