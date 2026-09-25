"""Restore the frozen RedMulE dependency closure outside the read-only submodule."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from agcws.core.config import ROOT as _REPO_ROOT
from agcws.designs.assets import asset_path

ROOT = _REPO_ROOT
PIN = "7fa9fbe8a29e8572810ae12b92c19749045ac860"
TARGETS = ("rtl", "redmule_hwpe", "redmule_test_hwpe", "cv32e40p_exclude_tracer", "cv32e40p_use_ff_regfile")


def container_sources(text, root):
    output = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("+define+"):
            output.append(line)
            continue
        prefix = "+incdir+" if line.startswith("+incdir+") else ""
        path = Path(line.removeprefix(prefix)).resolve()
        if not path.exists():
            raise ValueError(f"unresolved source path: {path}")
        output.append(prefix + "/workspace/.dependencies/" + str(path.relative_to(root)))
    return "\n".join(output) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bender", default=os.environ.get("AGCWS_BENDER", "bender"))
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.relative_to(ROOT / "out")
    if out == ROOT / "out":
        parser.error("use a dedicated directory below out/")
    version = subprocess.check_output([args.bender, "--version"], text=True).strip()
    if version != "bender 0.32.1":
        raise ValueError(f"frozen dependency preparation requires bender 0.32.1, got {version}")
    upstream = ROOT / "benchmarks/redmule"
    if subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip() != PIN:
        raise ValueError("RedMulE checkout differs from the validated pin")
    lock = asset_path("redmule", "Bender.lock").read_bytes()
    out.mkdir(parents=True, exist_ok=False)
    checkout = out / "rtl"
    subprocess.run(["git", "clone", "--no-hardlinks", "--no-checkout", str(upstream), str(checkout)], check=True)
    subprocess.run(["git", "-C", str(checkout), "checkout", "--detach", PIN], check=True)
    (checkout / "Bender.lock").write_bytes(lock)
    command = [args.bender, "-d", str(checkout), "script", "verilator"]
    for target in TARGETS:
        command.extend(["-t", target])
    command.extend(["-D", "COREV_ASSERT_OFF", "-D", "PACE_ENABLED", "-e", "cv32e40x"])
    with (out / "dependency.log").open("w") as log:
        sources = subprocess.check_output(command, text=True, stderr=log)
    if (checkout / "Bender.lock").read_bytes() != lock:
        raise ValueError("Bender changed the frozen dependency lock; preparation rejected")
    dependencies = {}
    locked_revisions = {value.decode() for value in re.findall(rb"revision: ([0-9a-f]{40})", lock)}
    for path in sorted((checkout / ".bender/git/checkouts").iterdir()):
        if not path.is_dir():
            continue
        revision = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
        if revision not in locked_revisions:
            raise ValueError(f"unlocked dependency checkout: {path.name} {revision}")
        dependencies[path.name] = revision
    if not dependencies:
        raise ValueError("Bender did not materialize dependency checkouts")
    rendered = container_sources(sources, out)
    (out / "sources.vlt").write_text(rendered)
    (out / "preparation.json").write_text(json.dumps({"redmule_commit": PIN, "bender": version,
        "lock_sha256": hashlib.sha256(lock).hexdigest(), "dependencies": dependencies,
        "sources_sha256": hashlib.sha256(rendered.encode()).hexdigest(), "targets": TARGETS,
        "defines": ["COREV_ASSERT_OFF", "PACE_ENABLED"], "excluded_package": "cv32e40x"}, indent=2) + "\n")
    print(json.dumps({"source_list": str(out / "sources.vlt"), "dependencies": len(dependencies)}))


if __name__ == "__main__":
    main()
