"""Shared cache for v4 annotated replays; failed proposals never receive scores."""

import fcntl
import json
import os
import subprocess
import time

import jsonschema

from experiments.ibex_temporal_v3.program import canonical, allocation
from experiments.ibex_temporal_v3.search import key


def measured(program, root, fingerprint):
    try:
        program = canonical(program)
    except jsonschema.ValidationError as exc:
        return {
            "valid": False,
            "stage": "SCHEMA",
            "reason": exc.message,
            "schema_path": list(exc.absolute_path),
        }, False
    except ValueError as exc:
        return {"valid": False, "stage": "PROTOCOL", "reason": str(exc)}, False
    identifier = key({"program": program, "measurement": fingerprint})
    locks = root / "locks"
    locks.mkdir(exist_ok=True)
    with (locks / f"{identifier}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        directory = root / "cache" / identifier
        record_path = directory / "result.json"
        if record_path.exists():
            return json.loads(record_path.read_text()), True
        directory.mkdir(parents=True, exist_ok=False)
        source = directory / "program.json"
        source.write_text(json.dumps(program, indent=2) + "\n")
        environment = {
            **os.environ,
            "AGCWS_CONTAINER_IMAGE": "agcws:window-validation-v1",
            "AGCWS_CONTAINER_OUTPUT": str(root.resolve()),
        }
        started = time.monotonic()
        with (directory / "driver.log").open("w") as log:
            result = subprocess.run(
                [
                    "bash",
                    "docker/run.sh",
                    "python3",
                    "-m",
                    "experiments.ibex_temporal_v4.evaluate",
                    "--program",
                    f"out/cache/{identifier}/program.json",
                    "--out",
                    f"out/cache/{identifier}/run",
                ],
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        output = directory / "run"
        if result.returncode:
            diagnostic = (directory / "driver.log").read_text()
            if (
                "useful work or observation window did not complete in time"
                in diagnostic
            ):
                record = {
                    "valid": False,
                    "stage": "USEFUL_WORK",
                    "reason": "body or fixed observation did not complete in the declared window",
                }
            elif "architectural reference mismatch" in diagnostic:
                record = {
                    "valid": False,
                    "stage": "FUNCTIONAL",
                    "reason": "architectural state mismatch",
                }
            else:
                raise RuntimeError(
                    f"evaluator infrastructure failed; inspect {directory}/driver.log"
                )
        else:
            profile = json.loads((output / "profile.json").read_text())
            record = {"valid": True, "stage": None, "reason": "", "profile": profile}
        feedback_path = output / "feedback.json"
        record["feedback"] = (
            json.loads(feedback_path.read_text()) if feedback_path.exists() else None
        )
        if record["valid"] and (
            record["feedback"] is None
            or any(
                record["feedback"][k] != record["profile"][k]
                for k in ("begin_tick", "end_tick")
            )
        ):
            raise RuntimeError("feedback is absent or differs from the activity window")
        execution_path = output / "execution.json"
        record["execution"] = (
            json.loads(execution_path.read_text()) if execution_path.exists() else None
        )
        if record["valid"] and record["execution"] is None:
            raise RuntimeError("execution diagnostics missing")
        record.update(
            cache_id=identifier,
            allocation=allocation(program),
            evaluation_s=time.monotonic() - started,
        )
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        return record, False
