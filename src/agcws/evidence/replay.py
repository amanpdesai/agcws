"""Read-only replay comparisons with explicit metadata exclusions."""

import hashlib
from pathlib import Path

from agcws.core.storage import read


def normalized(lines):
    digest = hashlib.sha256()
    date = []
    in_date = False
    header = True
    for line in lines:
        if header and line.strip() == "$date":
            if date or in_date:
                raise ValueError("duplicate date metadata")
            in_date = True
            continue
        if in_date:
            if line.strip() == "$end":
                in_date = False
            else:
                date.append(line.rstrip("\n"))
            continue
        if "$enddefinitions" in line:
            header = False
        digest.update(line.encode())
    if in_date or header:
        raise ValueError("incomplete waveform header")
    return {"semantic_stream_sha256": digest.hexdigest(), "date_metadata": date}


def comparable_measurement(row):
    return {k: row.get(k) for k in ("valid", "stage", "rates", "profile")}


def comparable_ibex(result):
    profile = result.get("profile")
    return {"valid": result["valid"], "stage": result["stage"],
            "profile": None if profile is None else {k: v for k, v in profile.items() if k != "extraction_s"},
            "allocation": result.get("allocation"), "feedback": result.get("feedback"),
            "execution": result.get("execution")}


def verify_frozen_inputs(root):
    root = root.resolve(strict=True)
    inventory = read(root / "freeze.json")
    for name, digest in inventory.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("unsafe frozen replay input path")
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError("frozen replay input escapes its root")
        with path.open("rb") as stream:
            checksum = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                checksum.update(block)
        if checksum.hexdigest() != digest:
            raise ValueError("frozen replay inputs changed")
    return len(inventory)
