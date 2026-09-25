import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator

from agcws.core.storage import read
from agcws.designs.temporal_registry import backend
from agcws.search.providers.gemini import generate
from agcws.search.providers.recovery import RecoveryMeter as Meter
from agcws.search.providers.schema import grammar, provenance


@pytest.mark.parametrize("domain", ["ibex-temporal", "aes-temporal", "dma-temporal", "mesh-temporal", "redmule-temporal"])
def test_runtime_projection_matches_verified_diagnostic(domain):
    schema = backend(domain).schema(2)
    original = copy.deepcopy(schema)
    frozen = json.loads(Path("tests/fixtures/provider_schema_golden.json").read_text())
    assert hashlib.sha256(json.dumps(grammar(schema), sort_keys=True).encode()).hexdigest() == frozen["sha256"][domain]
    assert schema == original


def test_sdk_gets_projected_grammar_but_native_bounds_remain(monkeypatch):
    schema = {"type": "array", "minItems": 2, "maxItems": 2,
              "items": {"type": "integer", "minimum": 1}}
    seen = []

    class Client:
        def __init__(self, **kwargs):
            self.models = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def generate_content(self, **kwargs):
            seen.append(kwargs)
            return SimpleNamespace(usage_metadata=SimpleNamespace(prompt_token_count=10,
                candidates_token_count=2, thoughts_token_count=1), candidates=[],
                model_version="test", prompt_feedback=None)

    monkeypatch.setattr("google.genai.Client", Client)
    generate("test", "flash-4096", "unchanged native context", schema)
    assert seen[0]["contents"] == "unchanged native context"
    assert seen[0]["config"]["response_json_schema"] == grammar(schema)
    assert not Draft202012Validator(schema).is_valid([0])
    assert Draft202012Validator(grammar(schema)).is_valid([0])


def test_schema_hashes_survive_api_error_and_block_mismatched_resume(tmp_path, monkeypatch):
    tmp_path = tmp_path / "study"
    tmp_path.mkdir()
    from google.genai.errors import APIError

    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test")
    schema = {"type": "integer", "minimum": 1}

    def reject(*args):
        raise APIError(400, {"error": {"message": "schema rejected"}}, None)

    monkeypatch.setattr("agcws.search.providers.recovery.generate", reject)
    meter = Meter(tmp_path, 1)
    directory = tmp_path / "panel/t/0/flash-4096/batches/003"
    with pytest.raises(RuntimeError, match="provider failure"):
        meter.call(directory, "flash-4096", "payload", schema, {"slot": 3})
    result = read(directory / "attempts/001/response.json")
    assert result["usage_unknown"] is True
    assert result["schema_provenance"] == provenance(schema)
    assert read(directory / "attempts/001/request_started.json")["schema_provenance"] == provenance(schema)
    assert meter.liability > 0
    # Explicitly acknowledge the pause in this isolated test before testing mismatch.
    (tmp_path.parent / "provider-paused.json").unlink()
    meter = Meter(tmp_path, 1)
    with pytest.raises(ValueError, match="checkpoint differs"):
        meter.call(directory, "flash-4096", "payload", {"type": "string"}, {"slot": 3})
