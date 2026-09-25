"""Dispatcher-facing API for strict RedMulE mapped replay."""

import json
import os
from pathlib import Path

from agcws.designs.redmule import gls


def synthesis_manifest(synthesis: Path) -> dict:
    """Publish the common manifest only for a checked mapped artifact."""
    synthesis = synthesis.resolve(strict=True)
    preparation = gls.verify_preparation(synthesis)
    mapped = json.loads((synthesis / "synthesis_manifest.json").read_text())
    for filename, field in (("mapped.v", "netlist_sha256"), ("mapped.json", "inventory_sha256"),
                            ("preparation.json", "preparation_sha256")):
        if gls.sha(synthesis / filename) != mapped[field]:
            raise ValueError(f"synthesis artifact differs: {filename}")
    source_root = Path(os.path.commonpath(list(preparation["sources"])))
    result = dict(top=gls.TOP, source_root=str(source_root),
                  sources={str(Path(path).relative_to(source_root)): digest
                           for path, digest in preparation["sources"].items()},
                  netlist_sha256=mapped["netlist_sha256"], liberty=preparation["liberty"],
                  liberty_sha256=preparation["liberty_sha256"],
                  parameters=gls.PARAMETERS, preparation_sha256=mapped["preparation_sha256"],
                  clock_port="clk_i", memory_policy=preparation["memory_policy"])
    path = synthesis / "manifest.json"
    if path.exists():
        existing = json.loads(path.read_text())
        # Upgrade our earlier absolute-path metadata only after comparing every
        # recorded identity; preserve the original manifest as evidence.
        legacy = {key: value for key, value in result.items() if key != "source_root"}
        legacy["sources"] = preparation["sources"]
        if existing == legacy:
            previous = synthesis / "manifest.absolute.json"
            if previous.exists() and previous.read_bytes() != path.read_bytes():
                raise ValueError("previous absolute manifest differs")
            if not previous.exists():
                previous.write_bytes(path.read_bytes())
            gls.write_json(path, result)
        elif existing != result:
            raise ValueError("existing standard synthesis manifest differs")
    else:
        gls.write_json(path, result)
    return result


def synthesize_trial(synthesis: Path) -> dict:
    """Map an already prepared design and publish its common manifest."""
    synthesis = synthesis.resolve(strict=True)
    gls.synthesize(synthesis, os.environ.get("AGCWS_YOSYS", "yosys"))
    return synthesis_manifest(synthesis)


def replay_trial(rtl: Path, synthesis: Path, out: Path, *, frozen_receipt: Path | None = None) -> dict:
    """Run matched GLS; return common window metadata only after strict success.

    Standard cell paths come from AGCWS_SKY130_CELL_MODELS and
    AGCWS_SKY130_PRIMITIVES. Optional frozen_receipt binds the
    independently verified frozen runtime receipt without replacing that check.
    """
    rtl, synthesis, out = rtl.resolve(strict=True), synthesis.resolve(strict=True), out.resolve()
    synthesis_manifest(synthesis)
    gls.replay(synthesis, rtl, out,
               Path(os.environ["AGCWS_SKY130_CELL_MODELS"]).resolve(strict=True),
               Path(os.environ["AGCWS_SKY130_PRIMITIVES"]).resolve(strict=True),
               os.environ.get("AGCWS_VERILATOR", "verilator"),
               os.environ.get("AGCWS_FST2VCD", "fst2vcd"),
               int(os.environ.get("AGCWS_REDMULE_GLS_JOBS", "4")),
               frozen_receipt.resolve(strict=True) if frozen_receipt is not None else None)
    receipt = json.loads((out / "gls_receipt.json").read_text())
    result = dict(waveform=str(out / "activity.vcd"), rtl_waveform=str(rtl / "activity.vcd"),
                  clock=gls.CLOCK, rtl_clock=gls.CLOCK, scope=gls.SCOPE.replace(".", "/"),
                  clock_port="clk_i", clock_edges=receipt["window"]["clock_edges"],
                  bounds=None, expected_period_s=1e-9,
                  dispatcher_sha256=gls.sha(Path(__file__)),
                  receipt=str(out / "gls_receipt.json"))
    gls.write_json(out / "matched_replay.json", result)
    return result
