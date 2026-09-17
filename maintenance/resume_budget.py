"""Resume frozen runs with an explicit accounting-only reservation adjustment."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline import engine
from agcws.pipeline.meter import Meter
from agcws.pipeline.model import cost, settings
from agcws.pipeline.storage import ensure, read
from agcws.provenance import file_sha256

VERSION = "observed-input-full-output-reserve-v1"


def reservation_bound(response, reserved, arm):
    """Keep unknown output at its frozen maximum; never infer missing usage = 0."""
    if not response or response.get("api_error") or not response.get("usage_unknown"):
        return reserved
    usage = response.get("usage_fields") or {}
    incoming = usage.get("prompt_token_count")
    if type(incoming) is not int or not 0 <= incoming <= 200000:
        return reserved
    outgoing = usage.get("candidates_token_count")
    limit = settings(arm)["max_output_tokens"]
    if outgoing is not None and (type(outgoing) is not int or not 0 <= outgoing <= limit):
        return reserved
    return min(reserved, cost(arm, incoming, limit))


class ReconciledMeter(Meter):
    def __init__(self, root, ceiling, provider_workers=1):
        super().__init__(root, ceiling, provider_workers)
        for marker in root.glob("panel/*/*/*/batches/*/request_started.json"):
            response = marker.parent / "response.json"
            if not response.exists():
                continue
            self._settle(marker.parent, read(response), marker.parts[-4])
        if not math.isfinite(self.liability) or self.liability < 0:
            raise ValueError("invalid reconciled liability")

    def _settle(self, directory, response, arm):
        marker = read(directory / "request_started.json")
        reserved = marker["reservation_usd"]
        adjusted = reservation_bound(response, reserved, arm)
        if adjusted == reserved:
            return
        ensure(directory / "accounting-v1.json", {
            "version": VERSION, "response_sha256": file_sha256(directory / "response.json"),
            "request_sha256": file_sha256(directory / "request_started.json"),
            "original_reservation_usd": reserved, "conservative_liability_usd": adjusted,
            "usage_still_unknown": True, "billed_cost_verified": False,
        })
        self.liability += adjusted - reserved

    def _call(self, directory, arm, contents, schema, identity, api_error, transport_error):
        existed = (directory / "response.json").exists()
        response = super()._call(directory, arm, contents, schema, identity, api_error, transport_error)
        if not existed:
            with self.lock:
                self._settle(directory, response, arm)
        return response


def amendment(root):
    manifest = engine.verify_inputs(ROOT, root)
    if manifest["spec"]["policies"] != ["flash-lite-medium"]:
        raise ValueError("this reviewed amendment is scoped to Flash-Lite only")
    if (root / "complete.json").exists():
        raise ValueError("completed runs must not be resumed")
    return {
        "version": VERSION, "manifest_sha256": file_sha256(root / "manifest.json"),
        "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "unchanged_cap_usd": manifest["spec"]["cost_ceiling_usd"],
        "original_runtime_sources_verified": True,
        "scope": "Meter accounting only; no changes to provider requests, outcomes, tasks or manifests",
        "authorization": "2026-09-17 user requested budget fix and resume Mesh/RedMulE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-paid", action="store_true")
    args = parser.parse_args()
    if not args.execute or not args.allow_paid:
        parser.error("explicit --execute --allow-paid required")
    root = args.directory.resolve()
    receipt = amendment(root)
    ensure(root / "accounting-amendment-v1.json", receipt)
    print(json.dumps(receipt), flush=True)
    # The frozen source inventory is intentionally unchanged. Only this reviewed
    # administrative wrapper replaces the meter; engine.run retains its lock,
    # checkpoint replay, input verification and paid-execution guard.
    engine.Meter = ReconciledMeter
    engine.run(ROOT, root, allow_paid=True)


if __name__ == "__main__":
    main()
