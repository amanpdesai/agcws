"""Bound-free serving grammar; native workload validation stays authoritative."""

import copy

from agcws.pipeline.metrics import key

VERSION = "bounds-projection-v1"
BOUNDS = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
          "minItems", "maxItems", "uniqueItems", "minLength", "maxLength", "pattern"}


def grammar(schema):
    if isinstance(schema, bool):
        return schema
    if not isinstance(schema, dict):
        raise ValueError("schema object or boolean required")
    result = {}
    for name, value in schema.items():
        if name in BOUNDS:
            continue
        if name in ("properties", "$defs", "definitions", "patternProperties"):
            result[name] = {field: grammar(child) for field, child in value.items()}
        elif name in ("items", "additionalProperties", "not", "if", "then", "else"):
            result[name] = grammar(value)
        elif name in ("anyOf", "oneOf", "allOf", "prefixItems"):
            result[name] = [grammar(child) for child in value]
        else:
            result[name] = copy.deepcopy(value)
    return result


def provenance(schema):
    return {"projection": VERSION, "requested_response_schema_sha256": key(schema),
            "provider_schema_sha256": key(grammar(schema))}
