#!/usr/bin/env python3
"""Inventory inferred Yosys memories before they are lowered to logic."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parameter_int(value):
    """Decode Yosys JSON's binary parameter representation when present."""
    if isinstance(value, str) and value and set(value) <= {"0", "1"}:
        return int(value, 2)
    return value


def inventory(top: str, sources: list[Path], output: Path, *, yosys: str,
              slang_plugin: str | None = None, include_dirs: list[Path] | None = None,
              compat: bool = False) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    include_dirs = include_dirs or []
    source_text = " ".join(str(path) for path in sources)
    includes = " ".join(f"-I {path}" for path in include_dirs)
    if slang_plugin:
        read = f"plugin -i {slang_plugin}; read_slang --top {top} -D SYNTHESIS {includes} {source_text}"
    else:
        if compat:
            compat_dir = output.parent / "frontend_compat"
            compat_dir.mkdir(parents=True, exist_ok=True)
            converted = []
            for source in sources:
                target = compat_dir / source.name
                subprocess.run(["python3", str(REPO_ROOT / "scripts/yosys_sv_compat.py"),
                                str(source), str(target)], check=True)
                converted.append(target)
            source_text = " ".join(str(path) for path in converted)
        read = f"read_verilog -sv -DSYNTHESIS {includes} {source_text}"
    json_path = output.with_suffix(".rtlil.json")
    command = f"{read}; hierarchy -top {top}; proc; opt; memory -nomap; opt; write_json {json_path}"
    result = subprocess.run([yosys, "-Q", "-p", command], capture_output=True,
                            text=True, check=False)
    (output.parent / "yosys.log").write_text("STDOUT\n" + result.stdout +
                                              "\nSTDERR\n" + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Yosys memory inventory failed with code {result.returncode}")
    design = json.loads(json_path.read_text())
    memories = []
    for module_name, module in design.get("modules", {}).items():
        for cell_name, cell in module.get("cells", {}).items():
            cell_type = cell.get("type", "")
            if not cell_type.startswith("$mem"):
                continue
            parameters = cell.get("parameters", {})
            memories.append({
                "module": module_name,
                "name": cell_name,
                "type": cell_type,
                "width": parameter_int(parameters.get("WIDTH")),
                "size": parameter_int(parameters.get("SIZE")),
                "abits": parameter_int(parameters.get("ABITS")),
                "rd_ports": parameter_int(parameters.get("RD_PORTS")),
                "wr_ports": parameter_int(parameters.get("WR_PORTS")),
                "parameters": parameters,
            })
    record = {"top": top, "sources": [str(path) for path in sources],
              "memories": memories, "yosys": yosys,
              "slang_plugin": slang_plugin, "compat": compat}
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", required=True)
    parser.add_argument("--source", action="append", type=Path, required=True)
    parser.add_argument("--include", action="append", type=Path, default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--yosys", default=os.environ.get("AGCWS_YOSYS", "yosys"))
    parser.add_argument("--slang-plugin", default=os.environ.get("AGCWS_SLANG_PLUGIN"))
    parser.add_argument("--compat", action="store_true",
                        help="convert sources with the project Yosys compatibility frontend")
    args = parser.parse_args()
    record = inventory(args.top, args.source, args.out, yosys=args.yosys,
                       slang_plugin=args.slang_plugin, include_dirs=args.include,
                       compat=args.compat)
    print(json.dumps({"out": str(args.out), "memories": len(record["memories"])},
                     sort_keys=True))


if __name__ == "__main__":
    main()
