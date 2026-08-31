"""Environment-backed paths; secrets and machine-specific paths stay out of Git."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def _load_dotenv(path: Path = ROOT / ".env") -> None:
    """Load simple KEY=VALUE settings without making dotenv mandatory."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))

_load_dotenv()

def path_setting(name: str, default: str) -> Path:
    value = Path(os.environ.get(name, default)).expanduser()
    return value if value.is_absolute() else ROOT / value

VERILATOR = Path(os.environ.get("AGCWS_VERILATOR", "verilator")).expanduser()
YOSYS = Path(os.environ.get("AGCWS_YOSYS", "yosys")).expanduser()
OPENSTA = Path(os.environ.get("AGCWS_OPENSTA", "sta")).expanduser()
VCD2SAIF = Path(os.environ.get("AGCWS_VCD2SAIF", "vcd2saif")).expanduser()
IVERILOG = Path(os.environ.get("AGCWS_IVERILOG", "iverilog")).expanduser()
VVP = Path(os.environ.get("AGCWS_VVP", "vvp")).expanduser()
LIBERTY = path_setting("AGCWS_LIBERTY", "third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib")
LIBERTY_NANGATE45 = path_setting("AGCWS_LIBERTY_NANGATE45", "third_party/liberty/nangate45/Nangate45_typ.lib")
ARTIFACT_ROOT = path_setting("AGCWS_ARTIFACT_ROOT", "out")
