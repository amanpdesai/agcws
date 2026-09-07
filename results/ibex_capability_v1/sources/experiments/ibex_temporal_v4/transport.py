"""One metered Vertex request; no retry, candidate repair, or process alarm."""


def request(client, model, payload, settings, schema=None):
    config = {
        "temperature": settings["temperature"],
        "top_p": settings["top_p"],
        "thinking_config": {"thinking_budget": settings["thinking_budget"]},
        "max_output_tokens": settings["max_output_tokens"],
        "response_mime_type": "application/json",
    }
    if schema is not None:
        config["response_json_schema"] = schema
    response = client.models.generate_content(
        model=model, contents=payload, config=config
    )
    usage = response.usage_metadata
    candidates = response.candidates or []
    texts = [
        p.text
        for c in candidates
        for p in (c.content.parts if c.content else [])
        if getattr(p, "text", None) and not getattr(p, "thought", False)
    ]
    tokens_in = int(getattr(usage, "prompt_token_count", 0) or 0)
    output = int(getattr(usage, "candidates_token_count", 0) or 0)
    thinking = int(getattr(usage, "thoughts_token_count", 0) or 0)
    return {
        "raw_text": "".join(texts),
        "tokens_in": tokens_in,
        "tokens_out": output + thinking,
        "thinking_tokens": thinking,
        "usage_unknown": usage is None,
        "est_cost_usd": (
            tokens_in * settings["input_rate"]
            + (output + thinking) * settings["output_rate"]
        )
        / 1e6,
        "finish_reasons": [str(c.finish_reason) for c in candidates],
        "prompt_feedback": str(response.prompt_feedback)
        if response.prompt_feedback
        else None,
        "model_version": response.model_version,
    }


def client(project, location="global"):
    from google import genai
    from google.genai import types

    return genai.Client(
        vertexai=True,
        project=project,
        location=location,
        http_options=types.HttpOptions(
            timeout=120000, retry_options=types.HttpRetryOptions(attempts=1)
        ),
    )
