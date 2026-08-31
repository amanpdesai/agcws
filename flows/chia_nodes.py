"""CHIA-decorated, design-agnostic execution nodes.

The functions accept only serializable command/path data. Design semantics,
goals, and policy state remain in adapters and experiment drivers.
"""
from __future__ import annotations

from pathlib import Path

try:
    from chia.base.ChiaFunction import ChiaFunction
except ImportError:
    def ChiaFunction(**_options):
        def decorate(function):
            return function
        return decorate

from agcws.nodes.activity import parse_vcd
from agcws.nodes.simulate import run_simulator


@ChiaFunction(resources={"verilator": 1})
def simulate_node(command: list[str], output_dir: str, timeout_s: float = 300.0) -> dict:
    """Run a simulator task and return a serializable artifact description."""
    _, artifact = run_simulator(command, Path(output_dir), timeout_s)
    return {"waveform": str(artifact.waveform), "stdout": str(artifact.stdout),
            "stderr": str(artifact.stderr)}


@ChiaFunction(resources={"activity": 1})
def activity_node(waveform: str, output_file: str, clock_name: str = "clk_i",
                  windows: int = 16) -> dict:
    """Extract cycle and coarse-window toggles into a JSON artifact."""
    import json

    activity = parse_vcd(Path(waveform), clock_name=clock_name, windows=windows)
    output = Path(output_file)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(activity, indent=2, sort_keys=True) + "\n")
    return {"activity": str(output), "clock_edges": activity["clock_edges"],
            "total_transitions": activity["total_transitions"]}
