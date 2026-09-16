"""Four-call migration check, isolated from frozen study runners. No retries."""

import json
import os
import time
from pathlib import Path

from google import genai
from google.genai import types

from agcws import config  # noqa: F401
from agcws.pipeline.backends import backend
from agcws.pipeline.provider_schema import grammar
from agcws.pipeline.storage import ensure, read, write


def main():
    root = Path("out/gemini3-migration-smoke-v1")
    root.mkdir(exist_ok=True)
    manifest = read(Path("out/baselines-maxbin-v1/aes/manifest.json"))
    target = "confirmation-alternating"
    manifest.update(target_rates=manifest["spec"]["targets"][target],
                    scale=manifest["spec"]["scale"])
    design = backend("aes-temporal")
    goal = {"target_rates": manifest["target_rates"], "scale": manifest["scale"],
            "success": "Every absolute normalized bin residual must be <= 0.05"}
    arms = [[os.environ["AGCWS_GEMINI_ECONOMY_MODEL"], 0.30, 2.50],
            [os.environ["AGCWS_GEMINI_STRONG_MODEL"], 0.75, 3.75]]
    ensure(root / "protocol.json", {"models": arms, "target": target, "rounds": 2,
          "thinking_level": "MEDIUM", "max_output_tokens": 8192, "retry_attempts": 1,
          "cost_ceiling_usd": 2, "scope": "Stateless measured-history feedback; not a study arm",
          "measurement_manifest": manifest})
    client = genai.Client(vertexai=True, project=os.environ["AGCWS_GCP_PROJECT"], location="global",
                         http_options=types.HttpOptions(timeout=600000,
                             retry_options=types.HttpRetryOptions(attempts=1)))
    records, liability = [], 0.0
    for model, input_rate, output_rate in arms:
        history = []
        for turn in range(2):
            directory = root / model / str(turn)
            if (directory / "record.json").exists():
                row = read(directory / "record.json")
                records.append(row)
                liability += row.get("estimated_cost_usd", row["reserved_usd"])
                if "error" in row:
                    break
                response = read(directory / "response.json")
                text = "".join(p.get("text", "") for c in response.get("candidates", [])
                               for p in c.get("content", {}).get("parts", []) if not p.get("thought"))
                proposal = design.decode(text, 1)["slots"][0]
                history.append({**row["trial"], "slot": turn, "program": proposal["submitted"]})
                continue
            directory.mkdir(parents=True)
            payload = design.payload(history, goal, 1)
            # Reserve a full model context and output, conservatively, before calling.
            reserve = (1048576 * input_rate + 8192 * output_rate) / 1e6
            if liability + reserve > 2:
                raise RuntimeError("Smoke liability cap reached")
            liability += reserve
            write(directory / "input.json", json.loads(payload))
            row = {"model": model, "turn": turn, "requested_slots": 1,
                   "history_count": len(history), "reserved_usd": reserve}
            started = time.monotonic()
            try:
                response = client.models.generate_content(model=model, contents=payload,
                    config=types.GenerateContentConfig(response_mime_type="application/json",
                        response_json_schema=grammar(design.schema(1)), max_output_tokens=8192,
                        thinking_config=types.ThinkingConfig(thinking_level="MEDIUM")))
                write(directory / "response.json", response.model_dump(mode="json", exclude_none=True))
                usage = response.usage_metadata
                row["usage"] = usage.model_dump(mode="json") if usage else None
                if usage and usage.prompt_token_count is not None and usage.candidates_token_count is not None:
                    cost = (usage.prompt_token_count * input_rate +
                            (usage.candidates_token_count + (usage.thoughts_token_count or 0)) * output_rate) / 1e6
                    row["estimated_cost_usd"] = cost
                    liability += cost - reserve
                row["finish_reasons"] = [str(c.finish_reason) for c in response.candidates or []]
                text = "".join(p.text or "" for c in response.candidates or []
                               for p in (c.content.parts if c.content else []) if not p.thought)
                decoded = design.decode(text, 1)
                row["parse_error"] = decoded["response_error"]
                proposal = decoded["slots"][0]
                if proposal["submitted"] is None:
                    row["trial"] = {"valid": False, "stage": "SCHEMA", "reason": decoded["response_error"]}
                else:
                    row["trial"] = design.evaluate(proposal, turn, history, manifest, directory, "migration-smoke")
                trial = {**row["trial"], "slot": turn, "program": proposal["submitted"]}
                history.append(trial)
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
            row["wall_clock_s"] = time.monotonic() - started
            records.append(row)
            write(directory / "record.json", row)
            write(root / f"progress-{len(records)}.json", {"records": records,
                  "cost_plus_unknown_liability_usd": liability})
            print(json.dumps(row), flush=True)
            if "error" in row:
                break
    client.close()
    ensure(root / "complete.json", {"records": records, "cost_plus_unknown_liability_usd": liability})


if __name__ == "__main__":
    main()
