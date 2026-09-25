"""Freeze policy-blind finalists from completed unified-pipeline cells."""

import argparse
import gzip
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path

from agcws.designs.aes.gls import sha
from agcws.evidence.packs import PACK, read_selected
from agcws.evidence.packs import manifest as packed_manifest
from agcws.reporting.metrics import error, key, max_bin_error, summarize

SUPPORTED = {"aes-temporal", "dma-temporal", "ibex-temporal", "mesh-temporal", "redmule-temporal-long"}


def read(path):
    return json.loads(path.read_text())


def select(roots, allow_partial=False):
    cases, omitted, inputs, seen = [], [], {}, set()
    for root in roots:
        root = root.resolve(strict=True)
        manifest_path = root / "manifest.json"
        manifest = read(manifest_path)
        spec = manifest["spec"]
        inputs[str(manifest_path)] = sha(manifest_path)
        for target, seed, policy in itertools.product(
            spec["targets"], spec["seeds"], spec["policies"]
        ):
            identity = (spec["domain"], target, seed, policy)
            if identity in seen:
                raise ValueError(f"duplicate cell across roots: {identity}")
            seen.add(identity)
            cell = root / "panel" / target / str(seed) / policy
            label = dict(domain=spec["domain"], target=target, seed=seed, policy=policy)
            complete = cell / "complete.json"
            if not complete.is_file():
                if not allow_partial:
                    raise ValueError(f"incomplete cell: {cell}")
                omitted.append({**label, "reason": "incomplete"})
                continue
            inputs[str(complete)] = sha(complete)
            trials = []
            for path in sorted((cell / "batches").glob("*/trials.json")):
                inputs[str(path)] = sha(path)
                trials.extend(read(path))
            for trial in trials:
                if trial["valid"]:
                    loss = error(trial["rates"], spec["targets"][target], spec["scale"])
                    worst = max_bin_error(trial["rates"], spec["targets"][target], spec["scale"])
                    if not all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
                               for a, b in ((loss, trial["loss"]), (worst, trial["max_bin_error"]))):
                        raise ValueError(f"stored metrics differ: {cell}")
            summarize(trials, spec["budget"], spec["tolerance"],
                      stop_on_success=spec["stop_on_success"],
                      success_metric=spec["success_metric"])
            valid = [t for t in trials if t["valid"]]
            if not valid:
                omitted.append({**label, "reason": "no valid workload"})
                continue
            metric = "max_bin_error" if spec["success_metric"] == "max-bin" else "loss"
            best = min(valid, key=lambda t: (t[metric], t["loss"], t["slot"]))
            program = best["canonical_program"]
            replay_id = key({"domain": spec["domain"], "program": program,
                             "measurement": manifest["measurement_fingerprint"]})
            cases.append({**label, "id": key(label), "replay_id": replay_id,
                          "root": str(root), "manifest_sha256": sha(manifest_path),
                          "slot": best["slot"], "program": program,
                          "rates": best["rates"], "target_rates": spec["targets"][target],
                          "scale": spec["scale"], "loss": best["loss"],
                          "max_bin_error": best["max_bin_error"],
                          "activity_solved": best[metric] <= spec["tolerance"],
                          "gate_support": "supported" if spec["domain"] in SUPPORTED else "unsupported"})
    payload = {"version": "finalist-power-v1", "selection":
               "Minimum declared success error, then NRMSE, then earliest slot; no gate-power selection.",
               "partial": allow_partial, "inputs": inputs, "cases": cases, "omitted": omitted}
    return {**payload, "sha256": key(payload)}


def file_identity(path):
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


@lru_cache(maxsize=65536)
def verified_digest(path, identity):
    digest = sha(path)
    if file_identity(path) != identity:
        raise ValueError(f'frozen selection input changed while hashing: {path}')
    return digest


def verify(plan):
    if plan["sha256"] != key({k: v for k, v in plan.items() if k != "sha256"}):
        raise ValueError("finalist plan changed")
    for path, expected in plan["inputs"].items():
        source = Path(path).resolve(strict=True)
        if verified_digest(source, file_identity(source)) != expected:
            raise ValueError(f"frozen selection input changed: {path}")


def references(entries):
    """Recover named witnesses or explicit fixed-replay references, never by power."""
    cases, inputs, domains = [], {}, set()
    for entry in entries:
        root, bank_path, archive = (Path(entry[k]).resolve(strict=True) for k in ("run", "bank", "archive"))
        manifest_path = root / "manifest.json"
        measured_manifest, bank = read(manifest_path), read(bank_path)
        spec = measured_manifest["spec"]
        mode = entry.get("mode", "qualified-witness")
        if mode not in ("qualified-witness", "fixed-replay"):
            raise ValueError("unknown reference evidence mode")
        domain = spec["domain"]
        if domain in domains or bank["domain"] != domain or bank["calibration"]["scale"] != spec["scale"]:
            raise ValueError("reference bank domain/scale differs or repeats")
        domains.add(domain)
        requests = {(r["witness_case"] if mode == "qualified-witness" else f"{split_name}-{r['id']}"): r
                    for split_name, split in bank["splits"].items() for r in split["requests"]}
        if not set(spec["targets"]) <= requests.keys():
            raise ValueError("bank lacks an original witness for a requested task")
        names = [f"panel/{t}/result.json.gz" for t in spec["targets"]]
        records = read_selected(archive, names)
        inventory = packed_manifest(archive)
        for path in [manifest_path, bank_path, archive / PACK, *[archive / s for s in inventory["shards"]]]:
            inputs[str(path)] = sha(path)
        for target, member in zip(spec["targets"], names):
            request = requests[target]
            record = json.loads(gzip.decompress(records[member]))
            measurement = record["measurement"]
            if (record["id"] != target or not measurement["valid"]
                    or request["rates"] != spec["targets"][target]):
                raise ValueError("reference witness identity or target differs")
            if mode == "qualified-witness" and (not request["qualified"] or
                    measurement["cache_id"] != request["witness_cache_id"]):
                raise ValueError("qualified witness identity differs")
            rates = measurement["profile"]["window_rates"] if domain == "ibex-temporal" else measurement["rates"]
            loss = error(rates, request["rates"], spec["scale"])
            if mode == "qualified-witness" and not math.isclose(loss, request["witness_error"], rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError("reference witness activity error differs from qualification")
            label = dict(domain=domain, target=target, seed=None, policy=mode)
            worst = max_bin_error(rates, request["rates"], spec["scale"])
            cases.append({**label, "role": "power_reference", "reference_mode": mode,
                "qualification_pass": request["qualified"], "id": key(label),
                "replay_id": key({"domain": domain, "program": record["program"],
                                  "measurement": measured_manifest["measurement_fingerprint"]}),
                "root": str(root), "manifest_sha256": sha(manifest_path), "slot": None,
                "program": record["program"], "rates": rates, "target_rates": request["rates"],
                "scale": spec["scale"], "loss": loss, "max_bin_error": worst,
                "activity_solved": worst <= spec["tolerance"],
                "gate_support": "supported" if domain in SUPPORTED else "unsupported",
                "reference_source": {"bank": str(bank_path), "archive": str(archive), "member": member}})
    payload = {"version": "finalist-power-v1", "selection": "Original bank witnesses or explicitly named fixed-replay references; no power selection or feasibility inference.",
               "partial": False, "inputs": inputs, "cases": cases, "omitted": []}
    return {**payload, "sha256": key(payload)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--runs", nargs="+", type=Path)
    source.add_argument("--witnesses", type=Path, help="JSON entries with run, bank and archive paths")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args(argv)
    if args.witnesses and args.allow_partial:
        parser.error("witness selection cannot omit failed qualification identities")
    plan = references(read(args.witnesses)) if args.witnesses else select(args.runs, args.allow_partial)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(plan, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"selected": len(plan["cases"]), "omitted": len(plan["omitted"]),
                      "supported": sum(c["gate_support"] == "supported" for c in plan["cases"]),
                      "sha256": plan["sha256"]}))


if __name__ == "__main__":
    main()
