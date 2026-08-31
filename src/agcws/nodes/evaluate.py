from pathlib import Path
from agcws.nodes.commands import CommandResult, run_command
from agcws.nodes.power import PowerProfile, parse_opensta_power_file
from agcws.nodes.synthesize import NetlistArtifact
from agcws.nodes.activity import ActivityArtifact

def evaluate_power(command: list[str], netlist: NetlistArtifact, activity: ActivityArtifact, output_dir: Path) -> tuple[CommandResult, PowerProfile]:
    """Run OpenSTA for one candidate against a cached netlist."""
    for label, path in (("netlist", netlist.netlist), ("Liberty", netlist.liberty),
                        ("activity", activity.activity_file)):
        if not path.is_file():
            raise FileNotFoundError(f"missing {label} input: {path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(command, cwd=output_dir)
    report = output_dir / "power.rpt"
    if result.returncode != 0:
        raise RuntimeError(f"OpenSTA failed with exit code {result.returncode}: {result.stderr.strip()}")
    if not report.is_file():
        raise FileNotFoundError(f"OpenSTA did not produce expected report: {report}")
    profile = parse_opensta_power_file(
        report, provenance={"report": report.name, "fidelity": "synthesis"}
    )
    return result, profile
