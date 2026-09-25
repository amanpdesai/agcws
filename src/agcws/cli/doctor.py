"""Read-only local installation and tool discovery."""

import argparse
import importlib.util
import json
import shutil


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    from agcws.core import config

    tools = {name: shutil.which(str(getattr(config, name))) for name in
             ("VERILATOR", "YOSYS", "OPENSTA", "IVERILOG", "VVP", "FST2VCD")}
    result = {"workspace": str(config.ROOT), "tools": tools,
              "liberty_exists": config.LIBERTY.is_file(),
              "plotting_installed": importlib.util.find_spec("matplotlib") is not None,
              "matched_gls_domains": ["aes-temporal", "dma-temporal"],
              "no_api_or_tool_calls": True}
    print(json.dumps(result, indent=2))
    return result
