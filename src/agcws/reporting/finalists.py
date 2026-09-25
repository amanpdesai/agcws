"""Export frozen finalist activity and independently measured gate power, without unit mixing."""

import argparse
import csv
import json
from pathlib import Path

from agcws.designs.aes.gls import sha
from agcws.studies.finalists import read, verify


def collect(plan, directories):
    verify(plan)
    selected = {c["id"]: c for c in plan["cases"]}
    measured = {}
    for directory in directories:
        completion = read(directory / "complete.json")
        path = directory / "measurement.json"
        if sha(path) != completion["measurement_sha256"]:
            raise ValueError("measurement checkpoint changed")
        result = read(path)
        ident = result["case_id"]
        if result["plan_sha256"] != plan["sha256"] or ident not in selected:
            raise ValueError("measurement belongs to another selection")
        if result["activity"] != selected[ident]:
            raise ValueError("measurement activity does not match frozen finalist")
        if ident in measured:
            raise ValueError("duplicate measured case")
        measured[ident] = (result, str(path), sha(path))
    cases = []
    for case in plan["cases"]:
        result, path, digest = measured.get(case["id"], (None, None, None))
        cases.append({**case, "normalized_target": [v / case["scale"] for v in case["target_rates"]],
                      "normalized_achieved": [v / case["scale"] for v in case["rates"]],
                      "signed_residual": [(a-b) / case["scale"] for a, b
                                          in zip(case["rates"], case["target_rates"])],
                      "power_status": "measured" if result else (
                          "unsupported" if case["gate_support"] == "unsupported" else "not_measured"),
                      "power_w": result["gate_dynamic_power_w"] if result else None,
                      "energy_j": result["gate_dynamic_energy_j"] if result else None,
                      "measurement": path, "measurement_sha256": digest})
    return {"version": "finalist-report-v1", "plan_sha256": plan["sha256"],
            "selection_is_partial": plan["partial"], "cases": cases, "omitted": plan["omitted"],
            "coverage": {"selected": len(cases), "gate_measured": len(measured),
                         "omitted": len(plan["omitted"])},
            "claim": "Descriptive finalist profiles, not trajectory AUC or a power-target solve test."}


def plot(case, destination):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3 if case["power_w"] is not None else 2, 1,
                             figsize=(8, 7), sharex=True, layout="constrained")
    bins = list(range(1, 9))
    axes[0].plot(bins, case["normalized_target"], "o--", label="Requested activity")
    axes[0].plot(bins, case["normalized_achieved"], "o-", label="Achieved activity")
    axes[0].set_ylabel("Activity / frozen scale")
    axes[0].legend()
    axes[1].bar(bins, case["signed_residual"])
    axes[1].axhline(0, color="black", linewidth=.5)
    axes[1].set_ylabel("Signed normalized error")
    if case["power_w"] is not None:
        axes[2].plot(bins, [p * 1000 for p in case["power_w"]], "o-")
        axes[2].set_ylabel("Gate dynamic power (mW)")
        axes[2].set_title("Measured power; no power target implied")
    axes[-1].set_xlabel("Matched temporal bin")
    axes[-1].set_xticks(bins)
    fig.suptitle(f'{case["domain"]} / {case["target"]}\n{case["policy"]}, seed {case["seed"]}')
    fig.savefig(destination)
    plt.close(fig)


def export(report, out, plots=False):
    out.mkdir(parents=True, exist_ok=False)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    fields = ["id", "domain", "target", "seed", "policy", "slot", "loss", "max_bin_error",
              "activity_solved", "power_status", "measurement", "measurement_sha256"]
    with (out / "cases.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: case[k] for k in fields} for case in report["cases"])
    fields = ["case_id", "bin", "target_activity", "achieved_activity", "signed_residual",
              "gate_dynamic_power_w", "gate_dynamic_energy_j"]
    with (out / "bins.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case in report["cases"]:
            for i in range(8):
                writer.writerow(dict(zip(fields, [case["id"], i+1, case["target_rates"][i],
                    case["rates"][i], case["signed_residual"][i],
                    case["power_w"][i] if case["power_w"] is not None else None,
                    case["energy_j"][i] if case["energy_j"] is not None else None])))
    workloads = out / "workloads"
    workloads.mkdir()
    for case in report["cases"]:
        (workloads / f'{case["id"]}.json').write_text(json.dumps(case["program"], indent=2) + "\n")
        if plots:
            figures = out / "figures"
            figures.mkdir(exist_ok=True)
            plot(case, figures / f'{case["id"]}.png')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, nargs="*", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args(argv)
    report = collect(read(args.plan), args.measurements)
    export(report, args.out, args.plots)
    print(json.dumps(report["coverage"]))


if __name__ == "__main__":
    main()
