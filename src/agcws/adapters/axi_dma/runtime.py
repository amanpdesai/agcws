"""Strict loader for deterministic axi_dma harness results."""
from __future__ import annotations

import json
from pathlib import Path

from agcws.adapters.base import SimResult


def load_sim_result(manifest: Path) -> SimResult:
    """Load a successful harness result, rejecting incomplete evidence."""
    data = json.loads(manifest.read_text())
    simulation = data.get("simulation")
    if not isinstance(simulation, dict):
        raise ValueError("DMA manifest has no simulation result")
    required = ("terminated", "assertions_ok", "outputs_ok", "useful_work")
    if any(field not in simulation for field in required):
        raise ValueError("DMA simulation result is incomplete")
    transfers = data.get("transfers")
    if not isinstance(transfers, list) or any(
        not all(item.get(field) is True for field in ("terminated", "assertions_ok", "outputs_ok"))
        for item in transfers
    ):
        raise ValueError("DMA transfer result is incomplete")
    return SimResult(
        terminated=simulation["terminated"] is True,
        assertions_ok=simulation["assertions_ok"] is True,
        outputs_ok=simulation["outputs_ok"] is True,
        useful_work=float(simulation["useful_work"]),
        raw=data,
    )
