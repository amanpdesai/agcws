"""Frozen-context response-contract comparison, with no simulation or repair."""

import argparse
import hashlib
import json
import os
import subprocess
from importlib.metadata import version
from pathlib import Path

from agcws import config
from agcws.provenance import file_sha256
from experiments.ibex_temporal_v3.agent import TemporalAgent, prompt
from experiments.ibex_temporal_v4.contract import CONTRACT, decode, response_schema
from experiments.ibex_temporal_v4.evaluate import write
from experiments.ibex_temporal_v4.transport import client, request


def digest(data):
    return hashlib.sha256(data).hexdigest()


def freeze(root):
    root.mkdir(parents=True, exist_ok=False)
    previous = Path("results/ibex_temporal_v3_development")
    old = json.loads((previous / "manifest.json").read_text())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    sources = [
        *Path("experiments").glob("ibex_temporal_v*/*.py"),
        Path("docs/IBEX_TEMPORAL_V4_PLAN.md"),
        *Path("src/agcws/policies").glob("*.py"),
        Path("src/agcws/config.py"),
        Path("src/agcws/provenance.py"),
    ]
    hashes = {}
    for path in sources:
        committed = subprocess.check_output(["git", "show", f"{commit}:{path}"])
        if digest(committed) != file_sha256(path):
            raise ValueError(f"uncommitted source: {path}")
        hashes[str(path)] = file_sha256(path)
    agent = TemporalAgent(lambda *_: "", prompt(False, True), model=old["model"])
    agent.correction = True
    calls = []
    for index, (target, seed) in enumerate(
        (t, s) for t in old["targets"] for s in old["seeds"]
    ):
        history_path = (
            previous
            / "panel"
            / target
            / f"seed-{seed}"
            / "agent-correction/trials.jsonl"
        )
        history = [json.loads(l) for l in history_path.read_text().splitlines()][:6]
        for arm in (
            ("original", "contract") if index % 2 == 0 else ("contract", "original")
        ):
            system = prompt(False, True) + (
                "\n" + CONTRACT if arm == "contract" else ""
            )
            payload = agent.build_payload(
                None,
                {
                    "profile": old["targets"][target]["rates"],
                    "scale": old["scale"],
                    "tolerance": old["tolerance"],
                },
                history,
                2,
                system,
            )
            name = f"{target}-{seed}-{arm}"
            path = root / "inputs" / f"{name}.json"
            path.parent.mkdir(exist_ok=True)
            path.write_text(payload + "\n")
            calls.append(
                {
                    "name": name,
                    "target": target,
                    "seed": seed,
                    "arm": arm,
                    "payload_sha256": file_sha256(path),
                    "history_sha256": file_sha256(history_path),
                }
            )
    settings = {
        k: old[k]
        for k in (
            "model",
            "temperature",
            "top_p",
            "thinking_budget",
            "max_output_tokens",
            "input_rate",
            "output_rate",
        )
    }
    write(root / "schema.json", response_schema(2))
    write(
        root / "manifest.json",
        {
            "source_commit": commit,
            "sources": hashes,
            "v3_manifest_sha256": file_sha256(previous / "manifest.json"),
            "settings": settings,
            "packages": {k: version(k) for k in ("google-genai", "jsonschema")},
            "calls": calls,
            "requested_slots_per_call": 2,
            "schema_sha256": file_sha256(root / "schema.json"),
            "phase": "development-contract-only",
        },
    )


def verify(root):
    manifest = json.loads((root / "manifest.json").read_text())
    for path, expected in manifest["sources"].items():
        if file_sha256(Path(path)) != expected:
            raise ValueError(f"frozen source changed: {path}")
    for name, expected in manifest["packages"].items():
        if version(name) != expected:
            raise ValueError(f"package changed: {name}")
    for call in manifest["calls"]:
        if (
            file_sha256(root / "inputs" / f"{call['name']}.json")
            != call["payload_sha256"]
        ):
            raise ValueError("frozen payload changed")
    if file_sha256(root / "schema.json") != manifest["schema_sha256"]:
        raise ValueError("response schema changed")
    return manifest


def summarize(root):
    manifest = verify(root)
    reports = {}
    for arm in ("original", "contract"):
        records = [
            json.loads((root / "calls" / f"{c['name']}.json").read_text())
            for c in manifest["calls"]
            if c["arm"] == arm
        ]
        slots = [s for r in records for s in r["decoded"]["slots"]]
        reports[arm] = {
            "calls": len(records),
            "requested_slots": len(slots),
            "schema_valid": sum(s["canonical"] is not None for s in slots),
            "complete_response_adherence": sum(
                r["decoded"]["response_error"] is None for r in records
            ),
            "unknown_usage": sum(r["usage_unknown"] for r in records),
            "api_errors": sum("exception" in r for r in records),
            "tokens_in": sum(r["tokens_in"] for r in records),
            "tokens_out": sum(r["tokens_out"] for r in records),
            "est_cost_usd": sum(r["est_cost_usd"] for r in records),
        }
    c = reports["contract"]
    return {
        "arms": reports,
        "ready": c["schema_valid"] / c["requested_slots"] >= 0.9
        and c["unknown_usage"] == 0
        and c["api_errors"] == 0,
        "scope": "static response-contract development; no hardware/search-quality claim",
    }


def run(root):
    manifest = verify(root)
    committed = subprocess.check_output(
        ["git", "show", f"HEAD:{root / 'manifest.json'}"]
    )
    if digest(committed) != file_sha256(root / "manifest.json"):
        raise ValueError("commit the frozen manifest before calls")
    output = root / "calls"
    output.mkdir(exist_ok=False)
    config._load_dotenv()
    api = client(os.environ["AGCWS_GCP_PROJECT"])
    schema = json.loads((root / "schema.json").read_text())
    for call in manifest["calls"]:
        payload = (root / "inputs" / f"{call['name']}.json").read_text().rstrip("\n")
        try:
            result = request(
                api,
                manifest["settings"]["model"],
                payload,
                manifest["settings"],
                schema if call["arm"] == "contract" else None,
            )
        except Exception as exc:
            result = {
                "exception": type(exc).__name__,
                "message": str(exc),
                "raw_text": "",
                "usage_unknown": True,
                "tokens_in": 0,
                "tokens_out": 0,
                "est_cost_usd": 0,
            }
        result["decoded"] = decode(result["raw_text"], 2)
        result["call"] = call
        write(output / f"{call['name']}.json", result)
        print(
            call["name"],
            sum(s["canonical"] is not None for s in result["decoded"]["slots"]),
            flush=True,
        )
    write(root / "aggregate.json", summarize(root))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run", "summarize"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root)
    elif args.action == "run":
        run(args.root)
    else:
        print(json.dumps(summarize(args.root), indent=2))
