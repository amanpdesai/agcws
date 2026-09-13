"""Build and execute the unmodified BaseJump all-to-all reference with Verilator."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path


def validate_delivery(log, size):
    deliveries = [tuple(map(int, row)) for row in re.findall(
        r"\(x,y\)=\(\s*(\d+),\s*(\d+)\) receiving id=\s*(\d+)\.", log
    )]
    expected = {(x, y, sender) for x in range(size) for y in range(size)
                for sender in range(size * size)}
    if ("[BSG_FINISH] test successful." not in log
            or len(deliveries) != len(expected) or set(deliveries) != expected):
        raise ValueError("mesh reference did not deliver every source exactly once to every tile")
    return {"delivered_packets": len(deliveries), "expected_packets": len(expected),
            "duplicate_packets": 0, "complete": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, choices=(2, 3, 4), default=2)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("jobs must be positive")
    repo = Path(__file__).resolve().parents[1]
    dependency = repo / "third_party/basejump_stl"
    test = dependency / "testing/bsg_noc/bsg_mesh_router/all_to_all"
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sources = [
        Path(line.replace("$BASEJUMP_STL_DIR", str(dependency)))
        if line.startswith("$BASEJUMP_STL_DIR") else test / line
        for line in (test / "sv.include").read_text().splitlines() if line.strip()
    ]
    command = [
        os.environ.get("AGCWS_VERILATOR", "verilator"), "--binary", "--timing",
        "--assert", "-Wno-fatal", "--top-module", "testbench",
        "--Mdir", str(output / "obj"), "-j", str(args.jobs),
        f"-I{dependency / 'bsg_misc'}", f"-I{dependency / 'bsg_noc'}",
        f"-DNUM_X={args.size}", f"-DNUM_Y={args.size}", "-DDIMS_P=2",
        "-DRUCHE_X=0", "-DRUCHE_Y=0", "-DXY_ORDER=1", "-DDEPOPULATED=1",
        *map(str, sources),
    ]
    metadata = {
        "scope": "unmodified upstream all-to-all reference; not benchmark qualification",
        "mesh_size": args.size,
        "command": command,
        "verilator": subprocess.check_output([command[0], "--version"], text=True).strip(),
        "sources_sha256": {
            str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
    }
    (output / "invocation.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with (output / "build.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    with (output / "run.log").open("w") as log:
        subprocess.run([str(output / "obj/Vtestbench")], cwd=output,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    result = validate_delivery((output / "run.log").read_text(), args.size)
    (output / "functional.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "exit_status": 0, **result}))


if __name__ == "__main__":
    main()
