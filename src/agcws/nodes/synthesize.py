from dataclasses import dataclass
from pathlib import Path
from agcws.nodes.commands import CommandResult, run_command

@dataclass(frozen=True)
class NetlistArtifact:
    netlist: Path
    liberty: Path
    manifest: Path

def synthesize_once(command: list[str], output_dir: Path, liberty: Path) -> tuple[CommandResult, NetlistArtifact]:
    """Design-level task. Cache its manifest and never call per workload."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "synthesis.manifest"
    if manifest.exists():
        return CommandResult(command, 0, "cached synthesis\n", ""), NetlistArtifact(output_dir / "mapped.v", liberty, manifest)
    result = run_command(command, cwd=output_dir)
    if result.returncode == 0:
        manifest.write_text("synthesis complete\n")
    return result, NetlistArtifact(output_dir / "mapped.v", liberty, manifest)
