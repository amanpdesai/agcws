"""Environment-backed paths; secrets and machine-specific paths stay out of Git."""
import os
from pathlib import Path

def path_setting(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()

VERILATOR = path_setting("AGCWS_VERILATOR", "verilator")
YOSYS = path_setting("AGCWS_YOSYS", "yosys")
OPENSTA = path_setting("AGCWS_OPENSTA", "sta")
VCD2SAIF = path_setting("AGCWS_VCD2SAIF", "vcd2saif")
IVERILOG = path_setting("AGCWS_IVERILOG", "iverilog")
LIBERTY = path_setting("AGCWS_LIBERTY", "third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib")
LIBERTY_NANGATE45 = path_setting("AGCWS_LIBERTY_NANGATE45", "third_party/liberty/nangate45/Nangate45_typ.lib")
ARTIFACT_ROOT = path_setting("AGCWS_ARTIFACT_ROOT", "out")
