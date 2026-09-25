"""AES-specific lowering and independent completion check."""

import re

from agcws.core.storage import read, write
from agcws.designs.aes.temporal import AESTemporalAdapter
from agcws.designs.schedule_backend import ScheduleTemporal


class AesTemporal(ScheduleTemporal):
    clock_edges = 6774
    scope = "aes_core_smoke.dut"

    def adapter(self):
        return AESTemporalAdapter(self.contract)

    def invocation(self, program, attempt, relative):
        write(attempt / "workload.json", self.adapter().elaborate(program))
        return ["env", "AGCWS_VERILATOR=/usr/local/bin/verilator", "python3",
                "-m", "agcws.designs.aes.simulate", str(relative / "workload.json"),
                "--out", str(relative), "--bit-cycles", str(self.clock_edges)]

    def completed(self, attempt):
        match = re.search(r"AES_CORE_WORKLOAD_DONE blocks=(\d+)", (attempt / "run.log").read_text())
        if not match or int(match[1]) != self.contract.work_units:
            return {"valid": False, "stage": "FUNCTIONAL", "reason": "AES completion check failed"}
        return {"valid": True, "useful_work": int(match[1]),
                "provenance": read(attempt / "provenance.json")}
