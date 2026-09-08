import gzip
import itertools

import pytest

from analysis.ibex_depth_v1 import describe, text
from experiments.ibex_depth_v1.model import ARMS


def test_depth_pairing_and_equal_valid_keep_failures():
    cells = [
        {"target": t, "seed": s, "arm": a}
        for t, s, a in itertools.product(("t0", "t1"), (610, 611, 612), ARMS)
    ]
    manifest = {
        "cells": cells,
        "prefixes": [2, 4],
        "tolerance": 0.1,
        "seeds": [610, 611, 612],
        "targets": {"t0": {}, "t1": {}},
    }
    histories = {}
    for c in cells:
        histories[c["target"], c["seed"], c["arm"]] = [
            {
                "slot": i,
                "valid": i != 3,
                "loss": 0.2 if i != 3 else None,
                "stage": "SCHEMA" if i == 3 else None,
                "cache_id": "same" if i != 3 else None,
                "proposal_mode": "initial" if i <= 2 else c["arm"],
                "prediction_assessment": {"scorable": False},
            }
            for i in range(1, 5)
        ]
    output = describe(manifest, histories, [])
    p = output["prefixes"]["4"]
    assert p["arms"]["pro-4096"]["mean_auc"] == pytest.approx(0.6)
    assert p["arms"]["pro-4096"]["validity"] == {"VALID": 18, "SCHEMA": 6}
    assert p["arms"]["pro-4096"]["mean_censored_evaluations"] == 4
    assert all(r["matched_valid_count"] == 3 for r in p["equal_valid_secondary"])
    assert set(p["paired_seed_auc_differences"]["pro-4096-minus-random"].values()) == {
        0
    }
    histories.pop(next(iter(histories)))
    with pytest.raises(ValueError, match="incomplete"):
        describe(manifest, histories, [])


def test_compressed_evidence_is_lossless(tmp_path):
    original = 'specific tool log  \n{"x": 1}\n'
    (tmp_path / "record.log.gz").write_bytes(gzip.compress(original.encode(), mtime=0))
    assert text(tmp_path, "record.log") == original
