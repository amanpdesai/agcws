"""Exact guard-only migration from the verified pre-release mesh harness."""

import hashlib
import json
from pathlib import Path

from agcws.core import config
from agcws.designs.assets import asset_path
from agcws.designs.mesh.adapter import MeshTemporalAdapter
from agcws.evaluation.activity.known_bits import Observation, read_bits
from agcws.evaluation.power.frozen import verify_sources


def frozen_dependency_name(relative):
    """Resolve the one recorded BaseJump relocation, without relaxing hashes."""
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('unsafe frozen mesh dependency path')
    prefix = Path('benchmarks/support/basejump_stl')
    if relative.is_relative_to(prefix):
        return Path('third_party/basejump_stl') / relative.relative_to(prefix)
    return relative


def original_harness(current: bytes) -> bytes:
    """Invert precisely the four added guard lines, accepting no other rewrite."""
    first = b"`ifndef AGCWS_MESH_MAPPED\n"
    middle = b"endmodule\n`endif\n\n`ifndef SYNTHESIS\nmodule mesh_temporal;"
    last = b"endmodule\n`endif\n"
    if (not current.startswith(first) or current.count(middle) != 1
            or not current.endswith(last)):
        raise ValueError("mesh guard-only migration shape differs")
    return current[len(first):-len(last)].replace(
        middle, b"endmodule\n\nmodule mesh_temporal;") + b"endmodule\n"


def validate(waveform, workload, synthesis, provenance):
    from agcws.designs.mesh.gls import sha

    attempt = waveform.parent
    # The shared frozen bridge layout is scratch/cache/<id>/attempt-NNN.
    scratch = attempt.parent.parent.parent
    request_path = scratch / "replay-request.json"
    result_path = scratch / "replay-result.json"
    receipt_path = scratch / "replay-receipt.json"
    request = json.loads(request_path.read_text())
    result = json.loads(result_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    if (sha(request_path) != receipt["request_sha256"]
            or sha(result_path) != receipt["result_sha256"]):
        raise ValueError("frozen bridge receipt hashes differ")
    case, manifest = request["case"], request["manifest"]
    if (case["domain"] != "mesh-temporal" or manifest["spec"]["domain"] != "mesh-temporal"
            or sha(Path(case["root"]) / "manifest.json") != case["manifest_sha256"]
            or json.loads((Path(case["root"]) / "manifest.json").read_text()) != manifest):
        raise ValueError("frozen mesh study identity differs")
    runtime = verify_sources(manifest, Path(receipt["runtime"]))
    if (not result["valid"] or result["rates"] != case["rates"]
            or result["canonical_program"] != case["program"]
            or attempt.parent.name != result["cache_id"]
            or result["provenance"] != provenance
            or json.loads((attempt / "program.json").read_text()) != case["program"]
            or MeshTemporalAdapter().elaborate(case["program"]) != workload):
        raise ValueError("frozen mesh replay/workload identity differs")
    original = runtime / "third_party/harnesses/mesh_temporal.sv"
    current = asset_path("mesh", "mesh_temporal.sv")
    if original_harness(current.read_bytes()) != original.read_bytes():
        raise ValueError("frozen mesh harness differs beyond the four guard lines")
    hashes = provenance["sources_sha256"]
    for name, digest in hashes.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("unsafe frozen mesh source path")
        if manifest["sources"].get(name) != digest or sha(runtime / path) != digest:
            raise ValueError(f"frozen RTL source identity differs: {name}")
    for name, digest in synthesis["sources"].items():
        path = Path(name)
        if path == current.resolve():
            if sha(current) != digest or hashes.get("third_party/harnesses/mesh_temporal.sv") != sha(original):
                raise ValueError("frozen/current harness hash differs")
        elif path.name == "sv.include":
            relative = frozen_dependency_name(path.relative_to(config.ROOT))
            if sha(runtime / relative) != digest:
                raise ValueError("frozen source-list hash differs")
        elif hashes.get(str(frozen_dependency_name(path.relative_to(config.ROOT)))) != digest:
            raise ValueError(f"frozen/synthesis dependency differs: {name}")
    activity = read_bits(waveform, Observation("mesh_temporal.dut", "mesh_temporal.clk", 8200))
    recorded = json.loads((attempt / "activity.json").read_text())
    samples = activity["per_cycle_toggles"]
    rates = [sum(samples[i*1025:(i+1)*1025])/1025 for i in range(8)]
    if (activity != recorded or activity["clock_edges"] != 8200 or rates != case["rates"]):
        raise ValueError("frozen mesh waveform does not reproduce selected rates")
    return {"version": "mesh-guard-only-migration-v1", "case_id": case["id"],
            "runtime": str(runtime), "frozen_harness_sha256": sha(original),
            "mapped_harness_sha256": sha(current),
            "unguarded_harness_sha256": hashlib.sha256(original_harness(current.read_bytes())).hexdigest(),
            "rule": "Remove exactly four guard lines; all remaining DUT and driver bytes must match.",
            "rates": rates, "frozen_best_rates_match": True,
            "sink_period": workload["sink_period"], "sink_pause": workload["sink_pause"],
            "inputs": {str(p): sha(p) for p in (request_path, result_path, receipt_path,
                                                  original, current, Path(__file__), waveform)}}
