"""Explicit static measurement bridge for the reviewed deadline-only change."""

import argparse
import ast
import copy
import hashlib
import subprocess
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, source_inventory, verify_inputs
from agcws.pipeline.metrics import key
from agcws.pipeline.model import settings
from agcws.pipeline.storage import read, write

BASE = "5d79314db"
MODEL = "src/agcws/pipeline/model.py"


def normalized(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "settings":
            if not isinstance(node.body[0], ast.Return) or not isinstance(node.body[0].value, ast.Dict):
                raise ValueError("changes extend beyond transport settings")
            value = node.body[0].value
            pairs = [(k, v) for k, v in zip(value.keys, value.values, strict=True)
                     if not isinstance(k, ast.Constant) or k.value != "transport"]
            value.keys, value.values = map(list, zip(*pairs, strict=True))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "genai" and node.func.attr == "Client":
                node.keywords = [k for k in node.keywords if k.arg != "http_options"]
    return ast.dump(tree, include_attributes=False)


def check_sources(old, current, old_model, new_model):
    if set(old) != set(current):
        raise ValueError("source membership changed")
    if [p for p in old if old[p] != current[p]] != [MODEL]:
        raise ValueError("not a model-only source change")
    if hashlib.sha256(old_model).hexdigest() != old[MODEL]:
        raise ValueError("historical model source differs")
    if normalized(old_model) != normalized(new_model):
        raise ValueError("changes extend beyond transport settings")


def bridge(reference, bank_path, destination):
    old, bank = read(reference / "manifest.json"), read(bank_path)
    old_model = subprocess.check_output(["git", "show", f"{BASE}:{MODEL}"], cwd=ROOT)
    check_sources(old["sources"], source_inventory(ROOT, old["spec"]["domain"]),
                  old_model, (ROOT / MODEL).read_bytes())
    if old["measurement_fingerprint"] != key({"sources": old["sources"], "runtime": old["runtime"],
                                              "domain": old["spec"]["domain"]}):
        raise ValueError("historical fingerprint differs")
    if (bank["calibration"]["measurement_fingerprint"] != old["measurement_fingerprint"]
            or bank["domain"] != old["spec"]["domain"] or not bank["target_bank_qualified"]):
        raise ValueError("bank/reference mismatch")
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "spec.json", old["spec"])
    prepare(ROOT, destination / "spec.json", destination / "reference")
    current = verify_inputs(ROOT, destination / "reference")
    if current["runtime"] != old["runtime"] or current["schema"] != old["schema"]:
        raise ValueError("runtime or schema changed")
    receipt = {"kind": "static-transport-only-bridge", "simulation_calls": 0, "model_calls": 0,
               "old_manifest_sha256": hashlib.sha256((reference / "manifest.json").read_bytes()).hexdigest(),
               "old_bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
               "old_fingerprint": old["measurement_fingerprint"],
               "new_fingerprint": current["measurement_fingerprint"],
               "changed_sources": [MODEL], "old_model_sha256": old["sources"][MODEL],
               "new_model_sha256": current["sources"][MODEL],
               "transport": settings("flash-4096")["transport"],
               "scope": "measurement compatibility only; not equivalent provider timing or a new replay"}
    promoted = copy.deepcopy(bank)
    promoted["calibration"]["measurement_fingerprint"] = current["measurement_fingerprint"]
    promoted["transport_bridge"] = receipt
    promoted["full_study_ready"] = False
    write(destination / "bank.json", promoted)
    write(destination / "receipt.json", receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(bridge(args.reference, args.bank, args.destination))
