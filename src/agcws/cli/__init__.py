"""Dispatch public commands and load their implementations on demand."""

import argparse
import importlib
import os
from pathlib import Path

COMMANDS = {
    "study": {"prepare": ("agcws.cli.study", "prepare"),
              "run": ("agcws.cli.study", "run"),
              "status": ("agcws.cli.study", "status"),
              "export": ("agcws.cli.study", "export"),
              "verify": ("agcws.cli.study", "verify-export")},
    "benchmark": {"qualify": ("agcws.cli.benchmark", None),
                  "audit": ("agcws.reporting.benchmark_audit", None)},
    "power": {"select": ("agcws.studies.finalists", None),
              "run": ("agcws.evaluation.power.finalists", None),
              "collect": ("agcws.evaluation.power.panel", None)},
    "report": {"build": ("agcws.reporting.finalists", None),
               "power": ("agcws.reporting.power_reference", None),
               "audit-baselines": ("agcws.reporting.baselines", None),
               "audit-models": ("agcws.reporting.models", None)},
    "evidence": {"verify": ("agcws.cli.evidence", None),
                 "verify-bank": ("agcws.evidence.bit_bank", None),
                 "pack": ("agcws.evidence.study_archive", "pack"),
                 "restore": ("agcws.evidence.study_archive", "restore")},
    "paper": {"figures": ("agcws.reporting.paper", None)},
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="AGCWS workload studies and power validation")
    parser.add_argument("--workspace", type=Path, help="workspace containing inputs, .env and dependencies")
    groups = parser.add_subparsers(dest="group", required=True)
    doctor = groups.add_parser("doctor", add_help=False, help="inspect configuration without tool/API calls")
    doctor.set_defaults(handler="agcws.cli.doctor", prefix=None)
    for group, commands in COMMANDS.items():
        actions = groups.add_parser(group).add_subparsers(dest="action", required=True)
        for name, (handler, prefix) in commands.items():
            actions.add_parser(name, add_help=False).set_defaults(handler=handler, prefix=prefix)
    args, rest = parser.parse_known_args(argv)
    if args.workspace is not None:
        workspace = args.workspace.resolve(strict=True)
        os.environ["AGCWS_ROOT"] = str(workspace)
        os.chdir(workspace)
    module = importlib.import_module(args.handler)
    module.main(([args.prefix] if args.prefix else []) + rest)
