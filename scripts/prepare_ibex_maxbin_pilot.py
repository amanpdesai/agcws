"""Prepare the explicitly authorized maximum-bin pilot without reusing old trajectories."""

import math

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, source_inventory
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256


def main():
    prior = ROOT / "out/ibex-precision-pilot-v1"
    original = read(prior / "manifest.json")
    current = source_inventory(ROOT, "ibex-temporal")
    changed = {p for p in set(current) | set(original["sources"])
               if current.get(p) != original["sources"].get(p)}
    expected = {f"src/agcws/pipeline/{p}" for p in
                ("engine.py", "metrics.py", "spec.py", "policies/dispatch.py")}
    if changed != expected:
        raise ValueError(f"unexpected runtime changes: {changed}")
    liability = 0
    for name in ("ibex-four-arm-pilot-v1", "ibex-precision-pilot-v1"):
        root = ROOT / "out" / name
        for p in root.glob("panel/*/*/*/batches/*/request_started.json"):
            response = p.parent / "response.json"
            info = read(response) if response.exists() else None
            liability += (info["estimated_usd"] if info and not info["usage_unknown"]
                          else read(p)["reservation_usd"])
    ceiling = math.floor((10-liability)*100)/100
    if ceiling <= 0:
        raise ValueError("no remaining authorized liability")
    destination = ROOT / "results/ibex/maxbin-pilot-v1-plan"
    destination.mkdir(parents=True, exist_ok=False)
    spec = {**original["spec"], "name": "ibex-maxbin-pilot-v1", "success_metric": "max-bin",
            "tolerance": .05, "cost_ceiling_usd": ceiling}
    write(destination / "config.json", spec)
    root = ROOT / "out/ibex-maxbin-pilot-v1"
    manifest = prepare(ROOT, destination / "config.json", root)
    if manifest["runtime"] != original["runtime"]:
        raise ValueError("simulator or container changed")
    write(destination / "manifest.json", manifest)
    write(destination / "freeze.json", {
        "manifest_sha256": file_sha256(root / "manifest.json"),
        "previous_manifest_sha256": file_sha256(prior / "manifest.json"),
        "changed_sources": sorted(changed), "measurement_sources_unchanged": True,
        "prior_liability_usd": liability, "remaining_ceiling_usd": ceiling,
        "scope": "new stopping criterion/context; fresh exploratory run, old metrics preserved"})
    print(f"Prepared eight cells; remaining estimated-liability cap ${ceiling:.2f}")


if __name__ == "__main__":
    main()
