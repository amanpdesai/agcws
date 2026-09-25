"""Verify calibration replay identity; does not certify a new target bank."""

import hashlib

from agcws.core.config import ROOT
from agcws.core.storage import read
from agcws.studies.calibration import report
from agcws.studies.engine import verify_inputs


def audit(original, replay):
    current = verify_inputs(ROOT, replay)
    before, after = report(original), report(replay)
    if {k: v for k, v in before.items() if k != "measurement_fingerprint"} != {
            k: v for k, v in after.items() if k != "measurement_fingerprint"}:
        raise ValueError("normalization or calibration outcomes changed")
    paths = [sorted((root / "panel").glob("*/*/*/batches/*/trials.json")) for root in (original, replay)]
    rows = [[t for path in group for t in read(path)] for group in paths]
    if len(rows[0]) != 64 or len(rows[1]) != 64:
        raise ValueError("all 64 calibration slots required")
    for left, right in zip(*rows, strict=True):
        for field in ("slot", "program", "valid", "stage", "reason", "rates", "profile"):
            if left.get(field) != right.get(field):
                raise ValueError(f"calibration replay differs in {field}")
        if left["valid"]:
            activity = []
            for root, trial in ((original, left), (replay, right)):
                candidates = list((root / "cache" / trial["cache_id"]).glob("attempt-*/activity.json"))
                if len(candidates) != 1:
                    raise ValueError("exactly one recorded activity trace required")
                activity.append(read(candidates[0]))
            for field in ("clock_edges", "per_cycle_toggles", "window_toggles", "total_transitions"):
                if activity[0][field] != activity[1][field]:
                    raise ValueError(f"integer waveform activity differs in {field}")
    return {"cases": 64, "exact_integer_activity_match": True,
            "original_manifest_sha256": hashlib.sha256((original / "manifest.json").read_bytes()).hexdigest(),
            "replay_manifest_sha256": hashlib.sha256((replay / "manifest.json").read_bytes()).hexdigest(),
            "old_measurement_fingerprint": before["measurement_fingerprint"],
            "new_measurement_fingerprint": current["measurement_fingerprint"],
            "scope": "calibration identity only; target qualification is separate", "full_study_ready": False}
