from dataclasses import dataclass
from pathlib import Path
import subprocess

@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

def run_command(command: list[str], *, cwd: Path | None = None, timeout_s: float | None = None) -> CommandResult:
    """Run a tool task with captured output; callers decide retry policy."""
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                                   timeout=timeout_s, check=False)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"command timed out after {timeout_s}s"
        return CommandResult(command, 124, stdout, stderr)
    return CommandResult(command, completed.returncode, completed.stdout, completed.stderr)
