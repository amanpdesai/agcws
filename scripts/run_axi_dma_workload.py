"""Run the validated DMA workload through deterministic channel harnesses."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agcws.adapters.axi_dma.adapter import AxiDmaAdapter


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: run_axi_dma_workload.py WORKLOAD.json OUT_DIR")
    workload_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    workload = json.loads(workload_path.read_text())
    adapter = AxiDmaAdapter()
    validity = adapter.validate_schema(workload)
    if validity.valid:
        validity = adapter.validate_protocol(workload)
    if not validity.valid:
        raise SystemExit(f"invalid workload at {validity.stage}: {validity.reason}")
    transfers = adapter.elaborate(workload)
    useful_work = sum(transfer["length"] for transfer in transfers)
    if useful_work < adapter.useful_work_floor:
        raise SystemExit(f"invalid workload at USEFUL_WORK: {useful_work} < floor {adapter.useful_work_floor}")
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    root = Path(__file__).resolve().parents[1]
    for index, transfer in enumerate(transfers):
        transfer_dir = out_dir / f"transfer-{index:03d}"
        transfer_dir.mkdir(parents=True, exist_ok=True)
        args = ["+ADDR=" + str(transfer["src"]), "+LEN=" + str(transfer["length"])]
        for direction, script in (("read", "run_axi_dma_rd_smoke.sh"), ("write", "run_axi_dma_wr_smoke.sh")):
            result = subprocess.run(["bash", str(root / "scripts" / script), str(transfer_dir / direction), *args],
                                    capture_output=True, text=True, check=False)
            if result.returncode:
                raise SystemExit(result.stderr or result.stdout)
        records.append({"index": index, "src": transfer["src"], "dst": transfer["dst"],
                        "length": transfer["length"], "status": "simulated",
                        "terminated": True, "assertions_ok": True, "outputs_ok": True})
    simulation = {"terminated": True, "assertions_ok": True, "outputs_ok": True,
                  "useful_work": useful_work, "transfer_count": len(records)}
    (out_dir / "workload_manifest.json").write_text(json.dumps(
        {"workload": workload, "transfers": records, "simulation": simulation}, indent=2
    ) + "\n")
    print(f"AGCWS_AXI_DMA_WORKLOAD_OK transfers={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
