from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from agcws.nodes.commands import CommandResult, run_command

_LIBERTY_DIGESTS: dict[tuple[str, int, int], str] = {}

def liberty_digest(liberty: Path) -> str:
    key = (str(liberty), liberty.stat().st_size, liberty.stat().st_mtime_ns)
    if key not in _LIBERTY_DIGESTS:
        _LIBERTY_DIGESTS[key] = hashlib.sha256(liberty.read_bytes()).hexdigest()
    return _LIBERTY_DIGESTS[key]

@dataclass(frozen=True)
class NetlistArtifact:
    netlist: Path
    liberty: Path
    manifest: Path

def synthesize_once(command: list[str], output_dir: Path, liberty: Path, design_fingerprint: str) -> tuple[CommandResult, NetlistArtifact]:
    """Design-level task. Cache its manifest and never call per workload."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "synthesis.manifest"
    if not design_fingerprint:
        raise ValueError("design_fingerprint is required for safe synthesis caching")
    inputs = {"command": command, "design_fingerprint": design_fingerprint, "liberty_sha256": liberty_digest(liberty)}
    netlist = output_dir / "mapped.v"
    if (manifest.exists() and netlist.is_file()
            and json.loads(manifest.read_text()).get("inputs") == inputs):
        return CommandResult(command, 0, "cached synthesis\n", ""), NetlistArtifact(output_dir / "mapped.v", liberty, manifest)
    result = run_command(command, cwd=output_dir)
    if result.returncode == 0:
        if not netlist.is_file():
            raise FileNotFoundError(f"synthesis command did not produce expected netlist: {netlist}")
        manifest.write_text(json.dumps({"inputs": inputs}, indent=2) + "\n")
    return result, NetlistArtifact(output_dir / "mapped.v", liberty, manifest)
