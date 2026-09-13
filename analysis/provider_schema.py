"""Provider grammar projection; native validation remains authoritative."""

import copy

BOUNDS = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
          "minItems", "maxItems", "uniqueItems", "minLength", "maxLength", "pattern"}


def grammar(schema):
    if isinstance(schema, bool):
        return schema
    if not isinstance(schema, dict):
        raise ValueError("schema object or boolean required")
    result = {}
    for key, value in schema.items():
        if key in BOUNDS:
            continue
        if key in ("properties", "$defs", "definitions", "patternProperties"):
            result[key] = {name: grammar(child) for name, child in value.items()}
        elif key in ("items", "additionalProperties", "not", "if", "then", "else"):
            result[key] = grammar(value)
        elif key in ("anyOf", "oneOf", "allOf", "prefixItems"):
            result[key] = [grammar(child) for child in value]
        else:
            result[key] = copy.deepcopy(value)
    return result
