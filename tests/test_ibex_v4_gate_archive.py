import json
from pathlib import Path

import pytest

from agcws.provenance import file_sha256


@pytest.mark.parametrize(
    "directory", ["ibex_temporal_v4_gate", "ibex_temporal_v4_gate_tiny"]
)
def test_real_cpu_gate_evidence_is_complete_and_equivalent(directory):
    root = Path("results") / directory
    gate = json.loads((root / "gate.json").read_text())
    for path, digest in gate["evidence"].items():
        assert file_sha256(root / path) == digest
    assert (root / "original/loadable.bin").read_bytes() == (
        root / "annotated/loadable.bin"
    ).read_bytes()
    for filename, fields in (
        (
            "profile.json",
            (
                "window_bit_transitions",
                "clock_edges",
                "begin_tick",
                "end_tick",
                "markers",
            ),
        ),
        ("functional.json", ("expected", "marker_pcs")),
    ):
        a, b = [
            json.loads((root / kind / filename).read_text())
            for kind in ("original", "annotated")
        ]
        assert all(a[k] == b[k] for k in fields)
