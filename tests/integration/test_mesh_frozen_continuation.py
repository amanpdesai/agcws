"""Opt-in replay of a selected best frozen mesh continuation workload."""
import json
import os
from pathlib import Path

import pytest

from agcws.designs.mesh import gls
from agcws.evaluation.power.finalists import restore
from agcws.evaluation.power.frozen import replay
from agcws.evaluation.power.windows import evaluate
from agcws.evidence.retention import compact
from agcws.studies.finalists import select, verify


@pytest.mark.skipif(not os.environ.get("AGCWS_MESH_FROZEN_OUT"), reason="opt-in frozen EDA replay")
def test_frozen_best_rates_and_mapped_power():
    out = Path(os.environ["AGCWS_MESH_FROZEN_OUT"]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    study = Path("out/strong-continuation-v1/mesh").resolve()
    plan = select([study], allow_partial=True)
    verify(plan)
    # Deterministic completed cell; select() chooses its best charged trial.
    case = sorted(plan["cases"], key=lambda c: (c["target"], c["seed"], c["policy"]))[0]
    gls.write_json(out / "selection.json", plan)
    manifest = json.loads((study / "manifest.json").read_text())
    runtime = Path("out/release-runtimes/strong-f4f4c1b3cf").resolve()
    result = replay(case, manifest, runtime, out / "rtl")
    assert result["rates"] == case["rates"]
    attempts = list((out / "rtl/cache" / result["cache_id"]).glob("attempt-*"))
    assert len(attempts) == 1
    rtl = attempts[0]
    restore(rtl / "activity.vcd")
    synthesis = Path(os.environ["AGCWS_MESH_SYNTHESIS"]).resolve()
    prepared = gls.replay_trial(rtl, synthesis, out / "gls")
    power = evaluate(synthesis=synthesis, out=out / "power",
                     expected_edges=prepared.pop("clock_edges"), **prepared)
    assert power["switching_additivity_pass"]
    assert all(row["unannotated_pins"] == 0 for row in [power["full"], *power["windows"]])
    migration = json.loads((out / "gls/migration.json").read_text())
    assert migration["frozen_best_rates_match"] and migration["rates"] == case["rates"]
    gls.write_json(out / "complete.json", {"case_id": case["id"], "target": case["target"],
        "seed": case["seed"], "policy": case["policy"], "slot": case["slot"], "rates": case["rates"],
        "migration_sha256": gls.sha(out / "gls/migration.json"),
        "power_sha256": gls.sha(out / "power/power.json")})
    for path in (rtl / "activity.vcd", out / "gls/activity.vcd"):
        compact(path)
