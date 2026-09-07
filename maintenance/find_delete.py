"""Delete only revalidated waveform-plan entries using GNU find -delete."""

import argparse
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from maintenance.clean_artifacts import (
    REPO,
    active_references,
    checked_file,
    target_path,
)


def execute_find(paths, journal, input_path):
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("empty or duplicate exact-path list")
    with input_path.open("xb") as stream:
        stream.write(b"".join(os.fsencode(p) + b"\0" for p in paths))
    expected = {str(p) for p in paths}
    deleted = []
    command = [
        "find",
        "-P",
        "-files0-from",
        str(input_path.resolve()),
        "-maxdepth",
        "0",
        "-type",
        "f",
        "-delete",
        "-print0",
    ]
    with journal.open("x") as log, tempfile.TemporaryFile() as errors:
        log.write(
            json.dumps(
                {
                    "command": command,
                    "planned_files": len(paths),
                    "started": time.time(),
                }
            )
            + "\n"
        )
        log.flush()
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=errors
        ) as process:
            pending = b""
            while chunk := process.stdout.read1(65536):
                pending += chunk
                while b"\0" in pending:
                    raw, pending = pending.split(b"\0", 1)
                    path = os.fsdecode(raw)
                    if path not in expected:
                        raise ValueError(
                            "find returned an unexpected or duplicate path"
                        )
                    expected.remove(path)
                    deleted.append(path)
                    log.write(json.dumps({"deleted": path}) + "\n")
                log.flush()
            status = process.wait()
        errors.seek(0)
        error = errors.read().decode(errors="replace")
        log.write(
            json.dumps(
                {"exit_code": status, "deleted_files": len(deleted), "stderr": error}
            )
            + "\n"
        )
        log.flush()
        os.fsync(log.fileno())
    if status or pending or expected:
        raise RuntimeError(f"partial deletion; inspect {journal}: {error}")
    if any(p.exists() for p in paths):
        raise RuntimeError("a path reappeared; refuse further deletion")
    return deleted


def apply(plan_path, confirmed=False):
    plan = json.loads(plan_path.read_text())
    root = REPO / "out"
    if root.is_symlink() or plan["root"] != str(root) or not plan["targets"]:
        raise ValueError("wrong artifact root")
    targets = plan["targets"]
    for name in targets:
        target_path(root, name)
    if active_references(root, targets):
        raise ValueError("active process references these runs")
    tracked = set(
        subprocess.check_output(["git", "ls-files", "-z", "out"], cwd=REPO)
        .decode()
        .split("\0")
    )
    paths = [checked_file(root, entry, targets) for entry in plan["files"]]
    if any(str(p.relative_to(REPO)) in tracked for p in paths):
        raise ValueError("tracked file in deletion plan")
    blocked = [str(p) for p in paths if not os.access(p.parent, os.W_OK | os.X_OK)]
    total = sum(p.stat().st_blocks * 512 for p in paths)
    summary = {
        "plan": str(plan_path),
        "files": len(paths),
        "allocated_bytes": total,
        "permission_blocked_files": len(blocked),
        "targets": targets,
    }
    print(json.dumps(summary), flush=True)
    if not confirmed:
        return summary
    if blocked:
        raise PermissionError(
            "no deletion attempted; run the reviewed command with an authorized account"
        )
    for entry in plan["files"]:
        checked_file(root, entry, targets)
    if active_references(root, targets):
        raise ValueError("run became active")
    journal = plan_path.with_suffix(".find-deleted.jsonl")
    listing = plan_path.with_suffix(".find-input.nul")
    deleted = execute_find(paths, journal, listing)
    result = {
        **summary,
        "deleted_files": len(deleted),
        "reclaimed_allocated_bytes": total,
        "journal": str(journal),
        "retained": "All non-waveform files; no directory removal.",
    }
    with plan_path.with_suffix(".find-result.json").open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply(args.plan, args.apply)
