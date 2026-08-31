from pathlib import Path
from agcws.provenance import file_sha256
from agcws.nodes.commands import CommandResult, run_command
from agcws.nodes.power import (PowerProfile, parse_annotated_pin_count,
                               parse_annotation_summary, parse_opensta_power_file)
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
    annotation_count = parse_annotated_pin_count(report.read_text())
    annotation_summary = parse_annotation_summary(report.read_text())
    provenance = {
            "report": report.name,
            "fidelity": "synthesis",
            "netlist_sha256": file_sha256(netlist.netlist),
            "liberty_sha256": file_sha256(netlist.liberty),
            "activity_sha256": file_sha256(activity.activity_file),
        }
    if annotation_count is not None:
        provenance["annotated_pin_activities"] = str(annotation_count)
    if annotation_summary is not None:
        provenance.update({
            "annotated_pins": str(annotation_summary["annotated"]),
            "unannotated_pins": str(annotation_summary["unannotated"]),
            "annotation_fraction": str(annotation_summary["fraction"]),
        })
    profile = parse_opensta_power_file(report, provenance=provenance)
    return result, profile
