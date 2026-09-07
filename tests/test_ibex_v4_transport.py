from types import SimpleNamespace as NS

from experiments.ibex_temporal_v4.transport import request


def test_single_request_schema_and_separate_thinking_accounting():
    calls = []

    def generate(**kwargs):
        calls.append(kwargs)
        return NS(
            usage_metadata=NS(
                prompt_token_count=100,
                candidates_token_count=20,
                thoughts_token_count=10,
            ),
            candidates=[
                NS(
                    finish_reason="STOP",
                    content=NS(
                        parts=[
                            NS(text="private", thought=True),
                            NS(text='{"candidates":[]}', thought=False),
                        ]
                    ),
                )
            ],
            prompt_feedback=None,
            model_version="pinned",
        )

    settings = {
        "temperature": 0.7,
        "top_p": 0.95,
        "thinking_budget": 512,
        "max_output_tokens": 8192,
        "input_rate": 0.3,
        "output_rate": 2.5,
    }
    result = request(
        NS(models=NS(generate_content=generate)),
        "pinned",
        "payload",
        settings,
        {"type": "object"},
    )
    assert len(calls) == 1
    assert calls[0]["config"]["response_json_schema"] == {"type": "object"}
    assert result["tokens_out"] == 30
    assert result["raw_text"] == '{"candidates":[]}'
    assert not result["usage_unknown"]
