"""Explicit model selection and metering; no repairs or replacement models."""

from agcws.pipeline.provider_schema import VERSION, grammar

MODELS = {
    "pro-4096": "gemini-2.5-pro",
    "flash-4096": "gemini-2.5-flash",
    "flash-lite-medium": "gemini-3.5-flash-lite",
    "strong-medium": "gemini-3.8-flash",
    "strong-medium-32k": "gemini-3.8-flash",
}


def settings(arm):
    if arm in ("flash-lite-medium", "strong-medium", "strong-medium-32k"):
        return {
            "model": MODELS[arm], "thinking_level": "MEDIUM",
            "temperature": 0.7, "top_p": 0.95,
            "max_output_tokens": 32768 if arm == "strong-medium-32k" else 8192,
            "response_schema_projection": VERSION,
            "input_usd_per_million": 0.30 if arm == "flash-lite-medium" else 0.75,
            "output_usd_per_million": 2.50 if arm == "flash-lite-medium" else 3.75,
            "pricing_verified": "2026-09-17" if arm == "flash-lite-medium" else "2026-09-18",
            "transport": {"version": "vertex-deadline-v1", "timeout_ms": 600000,
                          "sdk_attempts": 1},
        }
    return {
        "model": MODELS[arm],
        "thinking_budget": 4096,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 16384,
        "response_schema_projection": VERSION,
        "transport": {"version": "vertex-deadline-v1", "timeout_ms": 600000,
                      "sdk_attempts": 1},
    }


def cost(arm, tokens_in, tokens_out):
    if arm not in MODELS or min(tokens_in, tokens_out) < 0:
        raise ValueError("known model and nonnegative token counts required")
    if arm in ("strong-medium", "strong-medium-32k"):
        incoming, outgoing = 0.75, 3.75
    elif arm in ("flash-4096", "flash-lite-medium"):
        incoming, outgoing = 0.3, 2.5
    elif tokens_in <= 200000:
        incoming, outgoing = 1.25, 10.0
    else:
        incoming, outgoing = 2.5, 15.0
    return (incoming * tokens_in + outgoing * tokens_out) / 1e6


def summarize_response(response, arm):
    usage = response.usage_metadata
    fields = ("prompt_token_count", "candidates_token_count", "thoughts_token_count")
    counts = {k: getattr(usage, k, None) for k in fields}
    known = all(type(v) is int and v >= 0 for v in counts.values())
    candidates = response.candidates or []
    text = "".join(
        part.text
        for candidate in candidates
        for part in (candidate.content.parts if candidate.content else [])
        if getattr(part, "text", None) and not getattr(part, "thought", False)
    )
    incoming = counts[fields[0]] if known else None
    outgoing = counts[fields[1]] + counts[fields[2]] if known else None
    return {
        "raw_text": text,
        "usage_fields": counts,
        "tokens_in": incoming,
        "tokens_out": outgoing,
        "thinking_tokens": counts[fields[2]],
        "usage_unknown": not known,
        "estimated_usd": cost(arm, incoming, outgoing) if known else None,
        "model_version": response.model_version,
        "finish_reasons": [str(c.finish_reason) for c in candidates],
        "prompt_feedback": str(response.prompt_feedback) if response.prompt_feedback else None,
    }


def generate(project, arm, contents, schema):
    from google import genai
    from google.genai import types

    s = settings(arm)
    with genai.Client(
        vertexai=True,
        project=project,
        location="global",
        http_options=types.HttpOptions(
            timeout=s["transport"]["timeout_ms"],
            retry_options=types.HttpRetryOptions(attempts=s["transport"]["sdk_attempts"]),
        ),
    ) as api:
        response = api.models.generate_content(
            model=s["model"],
            contents=contents,
            config={
                "temperature": s["temperature"],
                "top_p": s["top_p"],
                "thinking_config": ({"thinking_level": s["thinking_level"]}
                                    if "thinking_level" in s else
                                    {"thinking_budget": s["thinking_budget"]}),
                "max_output_tokens": s["max_output_tokens"],
                "response_mime_type": "application/json",
                "response_json_schema": grammar(schema),
            },
        )
    return summarize_response(response, arm)
