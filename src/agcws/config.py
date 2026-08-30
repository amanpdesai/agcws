"""Environment-backed paths; secrets and machine-specific paths stay out of Git."""
import os
from pathlib import Path

def path_setting(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()

VERILATOR = path_setting("AGCWS_VERILATOR", "verilator")
YOSYS = path_setting("AGCWS_YOSYS", "yosys")
OPENSTA = path_setting("AGCWS_OPENSTA", "sta")
IVERILOG = path_setting("AGCWS_IVERILOG", "iverilog")
LIBERTY = path_setting("AGCWS_LIBERTY", "")
ARTIFACT_ROOT = path_setting("AGCWS_ARTIFACT_ROOT", "out")
