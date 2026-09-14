"""Supplement strict binary-hash replay with complete date-normalized VCD comparison."""

import argparse
import concurrent.futures
import hashlib
import subprocess
from pathlib import Path

from agcws.pipeline.storage import read, write


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


def waveform(path):
    with subprocess.Popen(["fst2vcd", str(path)], stdout=subprocess.PIPE, text=True) as process:
        result = normalized(process.stdout)
        if process.wait() != 0:
            raise RuntimeError("waveform conversion failed")
    return result


def audit(corpus, replay):
    config = read(replay / "config.json")
    complete = read(replay / "run/complete.json")
    original = [t for p in sorted((corpus / "panel").rglob("trials.json")) for t in read(p)]
    if not len(original) == len(complete["results"]) == len(config["cases"]) == 64:
        raise ValueError("full original and replay corpus required")

    def compare(triple):
        old, case, new = triple
        if old["program"] != case["program"] or new["program"] != case["program"]:
            raise ValueError("program pairing differs")
        expected = case["expected"]
        result = new["measurement"]
        for field in ("valid", "stage", "allocation", "feedback", "execution"):
            if result.get(field) != expected[field]:
                raise ValueError(f"measurement differs: {case['id']}/{field}")
        if not result["valid"]:
            return {"id": case["id"], "invalid_stage_reproduced": result["stage"], "match": True}
        actual = {k: v for k, v in result["profile"].items() if k not in ("extraction_s", "waveform_sha256")}
        prior = {k: v for k, v in expected["profile"].items() if k != "waveform_sha256"}
        if actual != prior:
            raise ValueError("profile differs beyond file hash")
        left = corpus / "cache" / old["cache_id"] / "run/sim.fst"
        right = replay / "run/cache" / result["cache_id"] / "run/sim.fst"
        for path, expected_hash in ((left, expected["profile"]["waveform_sha256"]), (right, result["profile"]["waveform_sha256"])):
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if digest != expected_hash:
                raise ValueError("waveform differs from recorded raw hash")
        a, b = waveform(left), waveform(right)
        return {"id": case["id"], "original": a, "replay": b,
                "match": a["semantic_stream_sha256"] == b["semantic_stream_sha256"]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(compare, zip(original, config["cases"], complete["results"], strict=True)))
    return {"scope": "complete decoded waveforms compared after excluding only header date metadata",
            "strict_binary_replay_passed": complete["exact_measurement_match"],
            "cases": 64, "matched": sum(r["match"] for r in rows), "records": rows,
            "full_study_ready": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, audit(args.corpus, args.replay))
