#!/usr/bin/env python3
"""Validate non-secret Vertex agent configuration without making an API call."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path


def preflight(prompt: Path, project: str | None, model: str | None) -> dict:
    missing = []
    if not project:
        missing.append("AGCWS_GCP_PROJECT")
    if not model:
        missing.append("AGCWS_GEMINI_MODEL")
    if not prompt.is_file() or prompt.stat().st_size == 0:
        missing.append(str(prompt))
    return {
        "valid": not missing and importlib.util.find_spec("google.genai") is not None,
        "missing": missing,
        "genai_installed": importlib.util.find_spec("google.genai") is not None,
        "project": project,
        "model": model,
        "prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest()
        if prompt.is_file() else None,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=Path, default=root / "prompts/agent_system_v1.txt")
    parser.add_argument("--project", default=os.environ.get("AGCWS_GCP_PROJECT"))
    parser.add_argument("--model", default=os.environ.get("AGCWS_GEMINI_MODEL"))
    args = parser.parse_args()
    result = preflight(args.prompt, args.project, args.model)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
