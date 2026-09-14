"""Reproduce the configured server deadline without credentials or a paid call."""

import httpx
from google import genai
from google.auth.credentials import AnonymousCredentials

from agcws.pipeline.model import generate


def test_current_deadline_is_forwarded_to_vertex(monkeypatch):
    captured = []
    original_client = genai.Client

    def respond(request):
        captured.append(request)
        return httpx.Response(200, json={
            "candidates": [{"content": {"parts": [{"text": "{}"}], "role": "model"},
                            "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 1, "candidatesTokenCount": 1,
                              "thoughtsTokenCount": 0},
            "modelVersion": "gemini-2.5-flash",
        })

    with httpx.Client(transport=httpx.MockTransport(respond)) as transport:
        def client(**kwargs):
            kwargs["credentials"] = AnonymousCredentials()
            kwargs["credentials"].token = "offline-test-token"
            kwargs["http_options"].httpx_client = transport
            return original_client(**kwargs)

        monkeypatch.setattr(genai, "Client", client)
        result = generate("offline-test-project", "flash-4096", "test", {"type": "object"})

    assert len(captured) == 1
    assert captured[0].headers["X-Server-Timeout"] == "120"
    assert captured[0].extensions["timeout"]["read"] == 120
    assert result["usage_unknown"] is False
