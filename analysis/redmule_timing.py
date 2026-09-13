"""Audit release/completion alignment from existing RedMulE witness evidence."""

import argparse
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from agcws.adapters.redmule import RedmuleTemporalAdapter
from agcws.pipeline.storage import read, write


def summarize(values):
    return {"count": len(values), "minimum": min(values), "median": median(values),
            "maximum": max(values)}


def job_metrics(program, functional):
    releases = RedmuleTemporalAdapter().elaborate(program)
    jobs = functional["job_completions"]
    size = program["size"]
    if (functional["valid"] is not True or len(jobs) != len(releases)
            or functional["completed_jobs"] != len(jobs)
            or functional["useful_work"] != len(jobs)*size**3
            or functional["checked_outputs"] != len(jobs)*size**2
            or functional["useful_work"] < 1024):
        raise ValueError("functional record does not match workload")
    values = []
    previous = 0
    for index, (release, job) in enumerate(zip(releases, jobs, strict=True)):
        number, completion, errors = job
        if number != index or errors or not max(release, previous) <= completion < 65536:
            raise ValueError("invalid completion sequence")
        values.append({"release_to_completion_cycles": completion-release,
                       "previous_completion_after_release_cycles": max(0, previous-release),
                       "remaining_after_eligibility_cycles": completion-max(release, previous),
                       "crossed_requested_bin": completion//8192 != release//8192})
        previous = completion
    return values


def analyze(root):
    manifest = read(root / "manifest.json")
    if manifest["spec"]["domain"] != "redmule-temporal":
        raise ValueError("RedMulE evidence required")
    terminal = read(root / "complete.json")
    programs = {}
    invalid = Counter()
    digest = hashlib.sha256()

    def record(path):
        digest.update(str(path.relative_to(root)).encode()+b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        return read(path)

    record(root / "manifest.json")
    record(root / "complete.json")
    slots = 0
    for path in sorted((root / "panel").glob("*/*/*/batches/*/trials.json")):
        for trial in record(path):
            slots += 1
            if trial["valid"] is not True:
                invalid[trial["stage"]] += 1
                continue
            key = trial["cache_id"]
            if key in programs and programs[key] != trial["program"]:
                raise ValueError("cache identity has conflicting workloads")
            programs[key] = trial["program"]
    if slots != terminal["slots"]:
        raise ValueError("terminal proposal count differs")
    groups = defaultdict(list)
    counts = Counter()
    for key, program in sorted(programs.items()):
        cache = root / "cache" / key
        if record(cache / "result.json")["valid"] is not True:
            raise ValueError("valid trial has invalid cached result")
        matches = []
        for path in sorted(cache.glob("attempt-*/functional.json")):
            functional = record(path)
            if functional["valid"] is True:
                if record(path.parent / "program.json") != program:
                    raise ValueError("executed program differs from trial")
                matches.append(functional)
        if len(matches) != 1:
            raise ValueError("missing or ambiguous successful functional evidence")
        group = f"size_{program['size']}/{program['pattern']}"
        groups[group].extend(job_metrics(program, matches[0]))
        counts[group] += 1
    return {"scope": "descriptive timing audit of unique valid workloads; not hardware latency or policy inference",
            "limitations": "Completion includes software/reference overhead; starts are not recorded. Invalid runs are excluded from timing, counted separately. Search-selected samples are not an unbiased latency population.",
            "manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
            "input_evidence_sha256": digest.hexdigest(), "proposal_slots": slots,
            "invalid_slots_by_stage": dict(sorted(invalid.items())),
            "unique_valid_workloads": len(programs), "bin_cycles": 8192,
            "groups": {name: {"workloads": counts[name], "jobs": len(rows),
                              "crossed_requested_bin_fraction": sum(r["crossed_requested_bin"] for r in rows)/len(rows),
                              **{field: summarize([r[field] for r in rows]) for field in (
                                  "release_to_completion_cycles", "previous_completion_after_release_cycles",
                                  "remaining_after_eligibility_cycles")}}
                       for name, rows in sorted(groups.items())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, analyze(args.directory))


if __name__ == "__main__":
    main()
