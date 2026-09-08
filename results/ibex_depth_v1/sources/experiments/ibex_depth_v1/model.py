"""Explicit model selection and metering; no repairs or replacement models."""

ARMS = ("pro-4096", "flash-4096", "random", "coverage")
MODELS = {
    "pro-4096": "gemini-2.5-pro",
    "flash-4096": "gemini-2.5-flash",
}


def settings(arm):
    return {
        "model": MODELS[arm],
        "thinking_budget": 4096,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 16384,
    }


def cost(arm, tokens_in, tokens_out):
    if arm not in MODELS or min(tokens_in, tokens_out) < 0:
        raise ValueError("known model and nonnegative token counts required")
    if arm == "flash-4096":
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
        "prompt_feedback": str(response.prompt_feedback)
        if response.prompt_feedback
        else None,
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
            timeout=120000, retry_options=types.HttpRetryOptions(attempts=1)
        ),
    ) as api:
        response = api.models.generate_content(
            model=s["model"],
            contents=contents,
            config={
                "temperature": s["temperature"],
                "top_p": s["top_p"],
                "thinking_config": {"thinking_budget": s["thinking_budget"]},
                "max_output_tokens": s["max_output_tokens"],
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            },
        )
    return summarize_response(response, arm)
