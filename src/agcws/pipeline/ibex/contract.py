"""Programs and experimental notes have separate, explicit response channels."""

import copy
import json

import jsonschema

from agcws.pipeline.ibex.program import SCHEMA, canonical

CONTRACT = (
    'Return {"hypothesis": "brief prediction", "candidates": [PROGRAM, PROGRAM]}. '
    "Each PROGRAM directly contains registers, memory_seed, and segments. "
    "Do not wrap a candidate in program, reference_slot, feedback, or other history "
    "metadata. Return complete programs, not patches. The history is observations, "
    "not the output format."
)


def response_schema(n, predictions=False):
    if type(n) is not int or n < 1:
        raise ValueError("positive requested candidate count required")
    program = copy.deepcopy(SCHEMA)
    program.pop("$schema")
    properties = {
        "hypothesis": {"type": "string"},
        "candidates": {
            "type": "array",
            "minItems": n,
            "maxItems": n,
            "items": program,
        },
    }
    if predictions:
        properties["predictions"] = {
            "type": "array",
            "minItems": n,
            "maxItems": n,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["reference_slot", "changed_factor", "window_directions"],
                "properties": {
                    "reference_slot": {"type": "integer", "minimum": 1},
                    "changed_factor": {"type": "string"},
                    "window_directions": {
                        "type": "array",
                        "minItems": 8,
                        "maxItems": 8,
                        "items": {"type": "integer", "enum": [-1, 0, 1]},
                    },
                },
            },
        }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def _nonfinite(value):
    raise ValueError(f"nonfinite JSON number: {value}")


def decode(text, n, predictions=False):
    """Retain positional failures and charge all requested slots; never unwrap."""
    schema = response_schema(n, predictions)
    try:
        response = json.loads(text, parse_constant=_nonfinite)
    except (ValueError, TypeError) as exc:
        return {
            "response_error": str(exc),
            "hypothesis": None,
            "slots": [_missing("unparseable response") for _ in range(n)],
        }
    if not isinstance(response, dict) or not isinstance(response.get("candidates"), list):
        return {
            "response_error": "object with candidates array required",
            "hypothesis": None,
            "slots": [_missing("missing candidates array") for _ in range(n)],
        }
    candidates = response["candidates"]
    if len(candidates) > n:
        return {
            "response_error": "too many candidates",
            "hypothesis": response.get("hypothesis"),
            "slots": [_missing("oversized batch") for _ in range(n)],
        }
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(response))
    slots = []
    for i in range(n):
        if i >= len(candidates):
            slots.append(_missing("missing requested candidate"))
            continue
        item = {
            "submitted": candidates[i],
            "canonical": None,
            "program_error": None,
            "prediction": None,
            "prediction_error": None,
        }
        try:
            item["canonical"] = canonical(candidates[i])
        except (jsonschema.ValidationError, ValueError) as exc:
            item["program_error"] = str(
                exc.message if isinstance(exc, jsonschema.ValidationError) else exc
            )
        if predictions:
            notes = response.get("predictions")
            note = notes[i] if isinstance(notes, list) and i < len(notes) else None
            try:
                jsonschema.validate(note, schema["properties"]["predictions"]["items"])
                item["prediction"] = note
            except jsonschema.ValidationError as exc:
                item["prediction_error"] = exc.message
        slots.append(item)
    return {
        "response_error": errors[0].message if errors else None,
        "hypothesis": response.get("hypothesis"),
        "slots": slots,
    }


def _missing(reason):
    return {
        "submitted": None,
        "canonical": None,
        "program_error": reason,
        "prediction": None,
        "prediction_error": None,
    }
