"""Shared cache, accounting and fixed-window checks for schedule-driven designs."""

import fcntl
import os
import subprocess
import time
from pathlib import Path

from agcws.pipeline import schedules
from agcws.pipeline.metrics import error, key
from agcws.pipeline.storage import read, write
from agcws.workloads.schedule import ScheduleContract, expand_schedule, random_schedule


class ScheduleTemporal:
    binary_path = None
    contract = ScheduleContract(64, 6000)
    allowed_policies = ("random", "phase-random", "phase-ga", "flash-4096", "pro-4096")

    def adapter(self):
        raise NotImplementedError

    def invocation(self, program, attempt, relative):
        raise NotImplementedError

    def completed(self, attempt):
        raise NotImplementedError

    def canonical(self, program):
        return {"sequence": expand_schedule(program, self.contract)}

    def failed(self, attempt):
        return None

    def environment(self):
        return {}

    def schema(self, n):
        return schedules.response_schema(n, self.contract)

    def random(self, rng):
        return random_schedule(rng, self.contract)

    def propose_classical(self, arm, rng, slot, history):
        return schedules.propose_classical(arm, rng, history, self.contract)

    def payload(self, history, goal, n):
        return schedules.payload(self.adapter(), history, goal, n)

    decode = staticmethod(schedules.decode)

    def measured(self, program, root, manifest):
        adapter = self.adapter()
        for check in (adapter.validate_schema, adapter.validate_protocol):
            validity = check(program)
            if not validity.valid:
                return {"valid": False, "stage": validity.stage.value,
                        "reason": validity.reason}, False
        canonical = self.canonical(program)
        identifier = key({"program": canonical, "measurement": manifest["measurement_fingerprint"]})
        locks = root / "locks"
        locks.mkdir(exist_ok=True)
        with (locks / f"{identifier}.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            directory = root / "cache" / identifier
            result_path = directory / "result.json"
            if result_path.exists():
                return read(result_path), True
            directory.mkdir(parents=True, exist_ok=True)
            attempt = directory / f"attempt-{len(list(directory.glob('attempt-*'))) + 1:03}"
            attempt.mkdir()
            write(attempt / "program.json", canonical)
            relative = Path("out") / attempt.relative_to(root)
            command = self.invocation(canonical, attempt, relative)
            environment = {**os.environ, "AGCWS_CONTAINER_IMAGE": manifest["runtime"]["image_id"],
                           "AGCWS_CONTAINER_CHECKOUT": "1", "AGCWS_CONTAINER_OUTPUT": str(root.resolve()),
                           **self.environment()}
            started = time.monotonic()
            with (attempt / "driver.log").open("w") as log:
                result = subprocess.run(["bash", "docker/run.sh", *command], env=environment,
                                        stdout=log, stderr=subprocess.STDOUT, check=False)
            if result.returncode:
                failure = self.failed(attempt)
                if failure is None:
                    raise RuntimeError(f"replay failed; inspect {attempt}/driver.log and run.log")
                failure.update(cache_id=identifier, canonical_program=canonical,
                               evaluation_s=time.monotonic() - started)
                write(result_path, failure)
                return failure, False
            completion = self.completed(attempt)
            if not completion["valid"]:
                record = completion
            else:
                activity = read(attempt / "activity.json")
                samples, edges = activity["per_cycle_toggles"], activity["clock_edges"]
                if edges != self.clock_edges or len(samples) != edges:
                    raise RuntimeError("observation window differs from the fixed contract")
                bins = [samples[i * edges // 8:(i + 1) * edges // 8] for i in range(8)]
                rates = [sum(values) / len(values) for values in bins]
                record = {"valid": True, "stage": None, "reason": "", "rates": rates,
                          "profile": {"window_rates": rates, "clock_edges": edges,
                                      "useful_work": completion["useful_work"], "bin_edges": [len(v) for v in bins],
                                      "scope": self.scope, "fidelity": "activity",
                                      "window": "full trace including reset"},
                          "provenance": completion["provenance"]}
            record.update(cache_id=identifier, canonical_program=canonical,
                          evaluation_s=time.monotonic() - started)
            write(result_path, record)
            return record, False

    def evaluate(self, proposal, slot, history, manifest, root, mode):
        result, hit = self.measured(proposal["submitted"], root, manifest)
        rates = result.get("rates") if result["valid"] else None
        return {**result, "slot": slot, "rates": rates, "cache_hit": hit,
                "loss": error(rates, manifest["target_rates"], manifest["scale"]) if rates else None,
                "residual": [(a - b) / manifest["scale"] for a, b in
                             zip(rates, manifest["target_rates"])] if rates else None,
                "prediction": proposal.get("prediction"), "prediction_error": proposal.get("prediction_error"),
                "proposal_mode": mode}
