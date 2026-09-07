"""Optional Vertex-backed proposer with a strict, testable JSON boundary."""
from __future__ import annotations

import json
import hashlib
import os
import signal
import logging
from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from agcws.policies.agent import AgentPolicy

LOG = logging.getLogger(__name__)


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
    compact_history = []
    for trial in history[-32:]:
        workload = _jsonable(getattr(trial, "workload", trial))
        profile = _jsonable(getattr(trial, "profile", None))
        validity = _jsonable(getattr(trial, "validity", None))
        compact_history.append({"workload": workload, "achieved": profile,
                                "residual": _jsonable(getattr(trial, "loss", None)),
                                "validity": validity})
    return json.dumps({
        "system_prompt": system_prompt,
        "design": {"name": getattr(adapter, "name", "unknown"),
                   "summary": getattr(adapter, "design_summary", ""),
                   "schema": getattr(adapter, "workload_schema", {}),
                   "constraints_text": "\n".join(f"- {item}" for item in getattr(adapter, "protocol_constraints", ()))},
        "goal": _jsonable(goal),
        "history": compact_history,
        "batch_size": n,
    }, sort_keys=True)


def parse_candidates(text: str, n: int) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        candidates = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("agent response is not valid JSON") from exc
    if isinstance(candidates, dict) and isinstance(candidates.get("candidates"), list):
        candidates = candidates["candidates"]
    elif isinstance(candidates, dict) and isinstance(candidates.get("workloads"), list):
        candidates = candidates["workloads"]
    elif isinstance(candidates, dict) and isinstance(candidates.get("workload"), list):
        candidates = candidates["workload"]
    elif isinstance(candidates, dict) and "operations" in candidates:
        candidates = [candidates]
    elif isinstance(candidates, dict) and ("transfers" in candidates or "program" in candidates):
        candidates = [candidates]
    if not isinstance(candidates, list) or not candidates or len(candidates) > n:
        raise ValueError(f"agent response must be a JSON list of 1..{n} candidates")
    if not all(isinstance(candidate, dict) for candidate in candidates):
        raise ValueError("every candidate must be a JSON object")
    return candidates


class VertexAgent(AgentPolicy):
    """Use an injected text generator; Vertex SDK wiring is deliberately lazy."""

    name = "vertex-agent"
    claim_scope = "cross_design_agent"
    temperature = 0.7
    top_p = 0.95
    max_output_tokens = 4096
    proposal_attempts = 3
    thinking_budget = None

    def __init__(self, generate: Callable[[str, str], str | tuple[str, dict[str, int]]], system_prompt: str, *, model: str):
        self.system_prompt = system_prompt
        self.last_usage: dict[str, int] = {"tokens_in": 0, "tokens_out": 0}
        self.last_diagnostics: dict[str, object] = {}

        def propose(adapter, goal, history, n):
            self.last_usage = {"tokens_in": 0, "tokens_out": 0}
            self.last_diagnostics = {}
            payload = self.build_payload(adapter, goal, history, n, system_prompt)
            last_error = None
            for attempt in range(self.proposal_attempts):
                timeout_s = int(os.environ.get("AGCWS_VERTEX_TIMEOUT_S", "60"))
                previous = signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("Vertex request timed out")))
                signal.alarm(timeout_s)
                try:
                    generated = generate(model, payload)
                except Exception as exc:
                    last_error = exc
                    self.last_diagnostics = {'exception_type': type(exc).__name__,
                                             'message': str(exc), 'usage_unknown': True}
                    LOG.warning('Vertex generation failed: %s', self.last_diagnostics)
                    if "timeout" in type(exc).__name__.lower() or "timeout" in str(exc).lower():
                        return []
                    generated = None
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, previous)
                if generated is None:
                    if attempt == self.proposal_attempts - 1:
                        return []
                    payload = json.dumps({"repair_request": f"Return 1..{n} valid workloads only.",
                                          "error": str(last_error)})
                    continue
                if isinstance(generated, tuple):
                    text, usage = generated
                    self.last_usage["tokens_in"] += int(usage.get("tokens_in", 0))
                    self.last_usage["tokens_out"] += int(usage.get("tokens_out", 0))
                    self.last_diagnostics = usage.get("diagnostics", {})
                else:
                    text = generated
                try:
                    return parse_candidates(text, n)
                except ValueError as exc:
                    last_error = exc
                    LOG.warning("Vertex parse failure error=%s diagnostics=%s raw=%s",
                                exc, self.last_diagnostics, text[:4000])
                    if attempt == self.proposal_attempts - 1:
                        raise
                    payload = json.dumps({
                        "repair_request": f"Return 1..{n} valid workloads only.",
                        "error": str(exc),
                        "previous_response": text,
                    })
            raise last_error

        digest = hashlib.sha256(system_prompt.encode()).hexdigest()
        super().__init__(propose, model=model, prompt_hash=digest)

    build_payload = staticmethod(build_payload)

    @classmethod
    def from_vertex(cls, system_prompt: str, *, model: str, project: str, location: str = "global"):
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("install agcws[chia] to use VertexAgent") from exc
        timeout_ms = int(__import__("os").environ.get("AGCWS_VERTEX_TIMEOUT_MS", "60000"))
        retry_attempts = int(os.environ.get("AGCWS_VERTEX_RETRY_ATTEMPTS", "1"))
        client = genai.Client(vertexai=True, project=project, location=location,
                              http_options=types.HttpOptions(
                                  timeout=timeout_ms,
                                  retry_options=types.HttpRetryOptions(attempts=retry_attempts,
                                                                       initial_delay=1,
                                                                       max_delay=8)))

        def generate(model_name: str, payload: str) -> tuple[str, dict[str, int]]:
            thinking = ({"thinking_config": {"thinking_budget": cls.thinking_budget}}
                        if cls.thinking_budget is not None else {})
            response = client.models.generate_content(model=model_name, contents=payload,
                                                      config={
                                                          **thinking,
                                                          "temperature": cls.temperature,
                                                          "top_p": cls.top_p,
                                                          "max_output_tokens": cls.max_output_tokens,
                                                          "response_mime_type": "application/json",
                                                      })
            metadata = getattr(response, "usage_metadata", None)
            candidates = getattr(response, "candidates", None) or []
            finish_reason = getattr(candidates[0], "finish_reason", None) if candidates else None
            feedback = getattr(response, "prompt_feedback", None)
            thoughts = int(getattr(metadata, "thoughts_token_count", 0) or 0)
            diagnostics = {"finish_reason": str(finish_reason) if finish_reason is not None else None,
                           "prompt_feedback": str(feedback) if feedback is not None else None,
                           "raw_text": response.text or "",
                           "thoughts_token_count": thoughts,
                           "model_version": getattr(response, "model_version", None)}
            LOG.info("Vertex response diagnostics=%s", diagnostics)
            return response.text or "", {
                "tokens_in": int(getattr(metadata, "prompt_token_count", 0) or 0),
                "tokens_out": int(getattr(metadata, "candidates_token_count", 0) or 0) + thoughts,
                "diagnostics": diagnostics,
            }

        return cls(generate, system_prompt, model=model)
