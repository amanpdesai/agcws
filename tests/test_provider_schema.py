import copy
import runpy

from jsonschema import Draft202012Validator

grammar = runpy.run_path("analysis/provider_schema.py")["grammar"]


def test_provider_projection_never_replaces_native_legality():
    native = {"type": "object", "required": ["minimum"], "additionalProperties": False,
              "properties": {"minimum": {"type": "integer", "minimum": 1, "maximum": 8}}}
    original = copy.deepcopy(native)
    projected = grammar(native)
    assert native == original
    assert "minimum" in projected["properties"]
    assert Draft202012Validator(projected).is_valid({"minimum": 0})
    assert not Draft202012Validator(native).is_valid({"minimum": 0})
    assert not Draft202012Validator(projected).is_valid({"minimum": "zero"})
    assert not Draft202012Validator(projected).is_valid({"minimum": 1, "extra": 2})
