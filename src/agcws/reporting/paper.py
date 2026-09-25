"""Render explicitly selected, verified finalist profiles for the paper."""

import argparse
import hashlib
import json
from pathlib import Path

from agcws.reporting.finalists import collect, plot


def render(recipe_path, destination):
    raw = recipe_path.read_bytes()
    recipe = json.loads(raw)
    if set(recipe) != {"version", "plan", "measurements", "cases"} or recipe["version"] != 1:
        raise ValueError("expected a version-1 figure recipe")
    if not isinstance(recipe["cases"], list) or not recipe["cases"]:
        raise ValueError("explicit nonempty case selection required")
    if len(set(recipe["cases"])) != len(recipe["cases"]):
        raise ValueError("duplicate case selection")
    base = recipe_path.resolve().parent
    plan_path = (base / recipe["plan"]).resolve(strict=True)
    directories = [(base / name).resolve(strict=True) for name in recipe["measurements"]]
    report = collect(json.loads(plan_path.read_bytes()), directories)
    cases = {case["id"]: case for case in report["cases"]}
    if set(recipe["cases"]) - cases.keys():
        raise ValueError("selected case absent from verified plan")
    # Validate every input before creating output; never overwrite published figures.
    destination.mkdir(parents=True, exist_ok=False)
    figures = []
    for index, ident in enumerate(recipe["cases"]):
        filename = f"profile-{index + 1:02d}.pdf"
        path = destination / filename
        plot(cases[ident], path)
        figures.append({"file": filename, "case_id": ident,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "power_status": cases[ident]["power_status"]})
    receipt = {"version": 1, "recipe_sha256": hashlib.sha256(raw).hexdigest(),
               "plan_file_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
               "plan_sha256": report["plan_sha256"], "figures": figures,
               "measurements": [{"case_id": ident,
                                 "sha256": cases[ident]["measurement_sha256"]}
                                for ident in recipe["cases"]],
               "claim": report["claim"]}
    (destination / "provenance.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(render(args.recipe, args.out), indent=2))
