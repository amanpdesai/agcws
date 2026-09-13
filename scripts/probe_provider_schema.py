"""One metered transport-grammar diagnostic on a previously rejected request."""

import argparse
import hashlib
import json
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.meter import Meter
from agcws.pipeline.storage import ensure, read


def run(source, root):
    manifest = verify_inputs(ROOT, source)
    original = source / "panel/flat_control/8200/flash-4096/batches/003"
    if not read(original / "response.json").get("api_error"):
        raise ValueError("diagnostic requires a recorded provider rejection")
    projection = runpy.run_path(ROOT / "analysis/provider_schema.py")["grammar"]
    payload = read(original / "input.json")["payload"]
    native = manifest["schema"]
    identity = {"kind": "provider-grammar-probe-v1", "source_manifest_sha256": hashlib.sha256((source / "manifest.json").read_bytes()).hexdigest(),
                "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "projection_sha256": hashlib.sha256((ROOT / "analysis/provider_schema.py").read_bytes()).hexdigest()}
    ensure(root / "manifest.json", {"identity": identity, "native_schema": native,
                                    "provider_schema": projection(native), "payload": payload,
                                    "cost_ceiling_usd": .2, "calls_maximum": 1})
    directory = root / "panel/schema_probe/8200/flash-4096/batches/001"
    directory.mkdir(parents=True, exist_ok=True)
    response = Meter(root, .2).call(directory, "flash-4096", payload, projection(native), identity)
    design = backend(manifest["spec"]["domain"])
    decoded = design.decode(response["raw_text"], 2)
    validity = []
    for slot in decoded["slots"]:
        program = slot["submitted"]
        static = design.adapter().validate_schema(program)
        if static.valid:
            static = design.adapter().validate_protocol(program)
        validity.append({"valid": static.valid, "reason": static.reason})
    result = {"scope": "transport diagnosis, not an end-to-end agent run", "identity": identity,
              "api_error": response.get("api_error"), "usage_unknown": response["usage_unknown"],
              "estimated_usd": response["estimated_usd"], "native_static_validity": validity}
    ensure(root / "complete.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        parser.error("one paid diagnostic call requires --execute")
    print(json.dumps(run(args.source.resolve(), args.directory.resolve())))
