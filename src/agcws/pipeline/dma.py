"""DMA-specific lowering and reference-checked copy completion."""

from agcws.adapters.axi_dma.temporal import DmaTemporalAdapter
from agcws.pipeline.schedule_backend import ScheduleTemporal
from agcws.pipeline.storage import read, write


class DmaTemporal(ScheduleTemporal):
    clock_edges = 9216
    scope = "axi_dma"

    def adapter(self):
        return DmaTemporalAdapter(self.contract)

    def failed(self, attempt):
        path = attempt / "driver.log"
        if not path.exists():
            return None
        text = path.read_text()
        reasons = ("workload failed to complete within the declared observation horizon",
                   "declared wait schedule exceeds observation horizon")
        if any(f"AssertionError: {reason}" in text for reason in reasons):
            return {"valid": False, "stage": "FUNCTIONAL",
                    "reason": "workload did not complete within the fixed observation window"}
        return None

    def invocation(self, program, attempt, relative):
        lowered = self.adapter().elaborate(program)
        write(attempt / "workload.json", lowered["workload"])
        return ["env", "AGCWS_DMA_TEST_MODULE=axi_dma_pipelined_tb",
                f"AGCWS_DMA_OBSERVATION_CYCLES={self.clock_edges}",
                f"AGCWS_BIT_ACTIVITY_CYCLES={self.clock_edges}",
                f"AGCWS_DMA_TRAILING_IDLE={lowered['trailing_idle_cycles']}",
                "AGCWS_PYTHON=python3", "AGCWS_FST2VCD=fst2vcd", f"AGCWS_ACTIVITY_SCOPE={self.scope}",
                "bash", "scripts/run_axi_dma_coupled.sh", str(relative / "workload.json"), str(relative)]

    def completed(self, attempt):
        observed = read(attempt / "sim_build/observed.json")
        if (observed["read_descriptors"] != self.contract.work_units
                or observed["write_completions"] != self.contract.work_units
                or observed["useful_work_bytes"] != self.contract.work_units * 64):
            return {"valid": False, "stage": "FUNCTIONAL", "reason": "DMA completion check failed"}
        return {"valid": True, "useful_work": observed["useful_work_bytes"],
                "provenance": {**read(attempt / "manifest.json"), "observed": observed}}
