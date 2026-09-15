"""Policies choose proposals; only the common engine executes them."""

import json
import random

from agcws.pipeline.backends import backend
from agcws.pipeline.model import MODELS
from agcws.pipeline.policies.controls import Control
from agcws.pipeline.storage import ensure


class Policy:
    def __init__(self, arm, seed, spec, target, schema, meter):
        self.arm, self.spec, self.target = arm, spec, target
        self.schema, self.meter = schema, meter
        self.backend = backend(spec["domain"])
        self.rng = random.Random(seed)
        self.control = (
            Control(arm, seed, spec["budget"], target, spec["scale"])
            if arm.startswith("gest-") or arm == "ridge-screen"
            else None
        )

    def propose(self, history, directory, identity):
        offset = len(history)
        if self.control is not None:
            request = self.control.ask()
            ensure(directory / "decision.json", request)
            return request["proposals"]
        n = min(self.spec["batch_size"], self.spec["budget"] - offset)
        if self.arm in MODELS and offset:
            contents = self.backend.payload(
                history,
                {
                    "profile": self.target,
                    "scale": self.spec["scale"],
                    "tolerance": self.spec["tolerance"],
                    **({"success_metric": "max-bin", "acceptance":
                        "Every bin must satisfy abs(achieved-target)/scale <= tolerance. "
                        "RMSE remains the ranking score; it is not sufficient for success. "
                        "Use signed per-bin residuals to correct the worst interval."}
                       if self.spec.get("success_metric") == "max-bin" else {}),
                },
                n,
            )
            if len(contents.encode()) + len(json.dumps(self.schema).encode()) + 4096 > 200000:
                raise ValueError("payload exceeds declared bound; no silent truncation")
            ensure(directory / "input.json", {"identity": identity, "payload": contents})
            response = self.meter.call(directory, self.arm, contents, self.schema, identity)
            if not response.get("api_error") and response["model_version"] != MODELS[self.arm]:
                raise ValueError("provider model version changed")
            decoded = self.backend.decode(response["raw_text"], n)
            ensure(directory / "decoded.json", decoded)
            return [
                {
                    "slot": offset + j + 1,
                    "program": p["submitted"],
                    "selected": True,
                    "parents": [],
                    "prediction": p["prediction"],
                    "prediction_error": p["prediction_error"],
                    "api_error": response.get("api_error"),
                }
                for j, p in enumerate(decoded["slots"])
            ]
        proposals = []
        for j in range(n):
            slot = offset + j + 1
            if not offset or self.arm == "random":
                program, parents = self.backend.random(self.rng), []
            else:
                program, parents = self.backend.propose_classical(self.arm, self.rng, slot, history)
            proposals.append(
                {"slot": slot, "program": program, "selected": True, "parents": parents}
            )
        return proposals

    def observe(self, trials):
        if self.control is not None:
            self.control.tell(trials)
