"""Optional Vertex-backed proposer with a strict, testable JSON boundary."""
from __future__ import annotations

import json
import hashlib
from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from agcws.policies.agent import AgentPolicy


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def build_payload(adapter: Any, goal: Any, history: list[Any], n: int, system_prompt: str) -> str:
    return json.dumps({
        "system_prompt": system_prompt,
        "design": {"name": getattr(adapter, "name", "unknown"),
                   "schema": getattr(adapter, "workload_schema", {})},
        "goal": _jsonable(goal),
        "history": [_jsonable(trial) for trial in history[-32:]],
        "batch_size": n,
    }, sort_keys=True)


def parse_candidates(text: str, n: int) -> list[dict]:
    try:
        candidates = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("agent response is not valid JSON") from exc
    if not isinstance(candidates, list) or len(candidates) != n:
        raise ValueError(f"agent response must be a JSON list of exactly {n} candidates")
    if not all(isinstance(candidate, dict) for candidate in candidates):
        raise ValueError("every candidate must be a JSON object")
    return candidates


class VertexAgent(AgentPolicy):
    """Use an injected text generator; Vertex SDK wiring is deliberately lazy."""

    name = "vertex-agent"
    temperature = 0.7
    top_p = 0.95
    max_output_tokens = 4096

    def __init__(self, generate: Callable[[str, str], str | tuple[str, dict[str, int]]], system_prompt: str, *, model: str):
        self.system_prompt = system_prompt
        self.last_usage: dict[str, int] = {"tokens_in": 0, "tokens_out": 0}

        def propose(adapter, goal, history, n):
            payload = build_payload(adapter, goal, history, n, system_prompt)
            generated = generate(model, payload)
            if isinstance(generated, tuple):
                text, usage = generated
                self.last_usage = {
                    "tokens_in": int(usage.get("tokens_in", 0)),
                    "tokens_out": int(usage.get("tokens_out", 0)),
                }
            else:
                text = generated
                self.last_usage = {"tokens_in": 0, "tokens_out": 0}
            return parse_candidates(text, n)

        digest = hashlib.sha256(system_prompt.encode()).hexdigest()
        super().__init__(propose, model=model, prompt_hash=digest)

    @classmethod
    def from_vertex(cls, system_prompt: str, *, model: str, project: str, location: str = "global"):
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("install agcws[chia] to use VertexAgent") from exc
        client = genai.Client(vertexai=True, project=project, location=location)

        def generate(model_name: str, payload: str) -> tuple[str, dict[str, int]]:
            response = client.models.generate_content(model=model_name, contents=payload,
                                                      config={
                                                          "temperature": cls.temperature,
                                                          "top_p": cls.top_p,
                                                          "max_output_tokens": cls.max_output_tokens,
                                                          "response_mime_type": "application/json",
                                                      })
            metadata = getattr(response, "usage_metadata", None)
            return response.text or "", {
                "tokens_in": int(getattr(metadata, "prompt_token_count", 0) or 0),
                "tokens_out": int(getattr(metadata, "candidates_token_count", 0) or 0),
            }

        return cls(generate, system_prompt, model=model)
