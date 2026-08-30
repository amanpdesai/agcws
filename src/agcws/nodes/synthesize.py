from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from agcws.nodes.commands import CommandResult, run_command

@dataclass(frozen=True)
class NetlistArtifact:
    netlist: Path
    liberty: Path
    manifest: Path

def synthesize_once(command: list[str], output_dir: Path, liberty: Path, design_fingerprint: str = "unknown") -> tuple[CommandResult, NetlistArtifact]:
    """Design-level task. Cache its manifest and never call per workload."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "synthesis.manifest"
    inputs = {"command": command, "design_fingerprint": design_fingerprint, "liberty_sha256": hashlib.sha256(liberty.read_bytes()).hexdigest()}
    if manifest.exists() and json.loads(manifest.read_text()).get("inputs") == inputs:
        return CommandResult(command, 0, "cached synthesis\n", ""), NetlistArtifact(output_dir / "mapped.v", liberty, manifest)
    result = run_command(command, cwd=output_dir)
    if result.returncode == 0:
        manifest.write_text(json.dumps({"inputs": inputs}, indent=2) + "\n")
    return result, NetlistArtifact(output_dir / "mapped.v", liberty, manifest)
