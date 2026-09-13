"""Recompute plumbing evidence; this does not independently resimulate RTL."""

import gzip
import hashlib
import json
from pathlib import Path

import pytest

from agcws.pipeline.metrics import error, summarize


@pytest.mark.parametrize("domain,edges,work", [("aes", 6774, 64), ("dma", 12000, 4096),
                                              ("mesh_temporal", 8200, None)])
def test_archived_shared_panel(domain, edges, work):
    directory = Path("results/benchmark_readiness_v1") / domain
    data = (directory / "shared_panel.json.gz").read_bytes()
    description = json.loads((directory / "shared_panel_summary.json").read_text())
    assert hashlib.sha256(data).hexdigest() == description["archive_sha256"]
    bundle = json.loads(gzip.decompress(data))
    files = {name: json.loads(text) for name, text in bundle["files"].items()}
    spec = files["manifest.json"]["spec"]
    assert files["complete.json"]["slots"] == 16
    assert not any("response" in name for name in files)
    for arm in ("phase-random", "phase-ga"):
        seed = spec["seeds"][0]
        prefix = f"panel/plumbing_only/{seed}/{arm}"
        trials = [row for name, rows in sorted(files.items())
                  if name.startswith(prefix + "/batches/") and name.endswith("/trials.json")
                  for row in rows]
        expected = summarize(trials, 8, spec["tolerance"])
        summary = files[prefix + "/complete.json"]
        assert all(summary[k] == v for k, v in expected.items())
        assert summary["valid_slots"] == 8
        for row in trials:
            cache = "cache/" + row["cache_id"]
            record = files[cache + "/result.json"]
            profile = record["profile"]
            useful_work = work if work is not None else sum(p["packets"] for p in row["program"]["phases"])
            assert profile["clock_edges"] == edges and profile["useful_work"] == useful_work
            assert profile["fidelity"] == "activity"
            samples = files[cache + "/attempt-001/activity.json"]["per_cycle_toggles"]
            bins = [samples[i * edges // 8:(i + 1) * edges // 8] for i in range(8)]
            rates = [sum(values) / len(values) for values in bins]
            assert rates == profile["window_rates"] == row["rates"]
            assert row["loss"] == error(rates, spec["targets"]["plumbing_only"], spec["scale"])
            first_slot = ((row["slot"] - 1) // spec["batch_size"]) * spec["batch_size"] + 1
            assert all(parent < first_slot for parent in row["parents"])
