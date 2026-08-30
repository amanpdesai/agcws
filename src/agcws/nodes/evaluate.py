from pathlib import Path
from agcws.nodes.commands import CommandResult, run_command
from agcws.nodes.power import PowerProfile
from agcws.nodes.synthesize import NetlistArtifact
from agcws.nodes.activity import ActivityArtifact

def evaluate_power(command: list[str], netlist: NetlistArtifact, activity: ActivityArtifact, output_dir: Path) -> tuple[CommandResult, PowerProfile]:
    """Run OpenSTA for one candidate against a cached netlist."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raise NotImplementedError("OpenSTA report parsing is required before producing a valid PowerProfile")
