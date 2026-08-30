from pathlib import Path
from agcws.nodes.commands import CommandResult, run_command
from agcws.nodes.power import PowerProfile
from agcws.nodes.synthesize import NetlistArtifact
from agcws.nodes.activity import ActivityArtifact

def evaluate_power(command: list[str], netlist: NetlistArtifact, activity: ActivityArtifact, output_dir: Path) -> tuple[CommandResult, PowerProfile]:
    """Run OpenSTA for one candidate against a cached netlist."""
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(command, cwd=output_dir)
    return result, PowerProfile(0.0, 0.0, valid=result.returncode == 0, fidelity="synthesis", provenance={"netlist": str(netlist.netlist), "activity": str(activity.activity_file)})
