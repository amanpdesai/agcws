"""Simplify the Ibex response schema for serving while retaining full local validation."""

import copy

from agcws.designs.ibex.programs.contract import response_schema


def serving_schema(n, predictions=False):
    schema = copy.deepcopy(response_schema(n, predictions))
    program = schema["properties"]["candidates"]["items"]
    body = program["properties"]["segments"]["items"]["properties"]["body"]
    alternatives = body["items"]["oneOf"]
    body["items"] = {
        "type": "object",
        "required": ["op", "a"],
        "additionalProperties": False,
        "properties": {
            "op": {
                "type": "string",
                "enum": [a["properties"]["op"]["const"] for a in alternatives],
            },
            "a": {"type": "integer"},
            "b": {"type": "integer"},
            "dst": {"type": "integer"},
        },
    }

    def relax(value):
        if isinstance(value, dict):
            return {
                k: relax(v)
                for k, v in value.items()
                if k not in ("minimum", "maximum", "minItems", "maxItems")
            }
        if isinstance(value, list):
            return [relax(v) for v in value]
        return value

    return relax(schema)
