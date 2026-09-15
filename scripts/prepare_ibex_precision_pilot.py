"""Freeze the user-authorized 0.05 pilot within the original $10 model allowance."""

import math

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256


def main():
    original = ROOT / "out/ibex-four-arm-pilot-v1"
    manifest = verify_inputs(ROOT, original)
    for arm in ("flash-4096", "pro-4096"):
        for seed in (9500, 9501):
            read(original / "panel/confirmation-alternating" / str(seed) / arm / "complete.json")
    liability = 0.0
    for path in original.glob("panel/*/*/*/batches/*/request_started.json"):
        response = path.parent / "response.json"
        info = read(response) if response.exists() else None
        liability += (info["estimated_usd"] if info and not info["usage_unknown"]
                      else read(path)["reservation_usd"])
    ceiling = math.floor((10.0-liability)*100)/100
    if ceiling <= 0:
        raise ValueError("original authorization has no remaining headroom")
    destination = ROOT / "results/ibex/precision-pilot-v1-plan"
    destination.mkdir(parents=True, exist_ok=False)
    spec = {**manifest["spec"], "name": "ibex-precision-pilot-v1",
            "tolerance": .05, "cost_ceiling_usd": ceiling}
    write(destination / "config.json", spec)
    root = ROOT / "out/ibex-precision-pilot-v1"
    new = prepare(ROOT, destination / "config.json", root)
    if new["measurement_fingerprint"] != manifest["measurement_fingerprint"]:
        raise ValueError("precision pilot must preserve measurement identity")
    write(destination / "manifest.json", new)
    write(destination / "freeze.json", {
        "original_manifest_sha256": file_sha256(original / "manifest.json"),
        "manifest_sha256": file_sha256(root / "manifest.json"),
        "prior_liability_usd": liability, "remaining_ceiling_usd": ceiling,
        "combined_authorization_usd": 10.0,
        "scope": "exploratory precision pilot; same exposed target/seeds, fresh trajectories; no confirmatory inference"})
    print(f"Prepared eight cells; remaining model ceiling ${ceiling:.2f}")


if __name__ == "__main__":
    main()
