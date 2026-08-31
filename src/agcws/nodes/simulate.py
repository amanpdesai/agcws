from dataclasses import dataclass
from pathlib import Path
from agcws.nodes.commands import CommandResult, run_command

@dataclass(frozen=True)
class SimulationArtifact:
    waveform: Path
    stdout: Path
    stderr: Path
    cycles: int | None = None

def run_simulator(command: list[str], output_dir: Path, timeout_s: float) -> tuple[CommandResult, SimulationArtifact]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(command, cwd=output_dir, timeout_s=timeout_s)
    stdout = output_dir / "sim.stdout"
    stderr = output_dir / "sim.stderr"
    stdout.write_text(result.stdout)
    stderr.write_text(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f"simulator failed with exit code {result.returncode}: {result.stderr.strip()}"
        )
    waveform = output_dir / "activity.vcd"
    if not waveform.is_file():
        raise FileNotFoundError(f"simulator did not produce expected waveform: {waveform}")
    return result, SimulationArtifact(waveform, stdout, stderr)
