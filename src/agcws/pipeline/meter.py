"""Durable paid-call reservations and serialized provider access."""

import os
import threading
import time

from agcws.pipeline.model import cost, generate, settings
from agcws.pipeline.storage import read, write


class Meter:
    def __init__(self, root, ceiling):
        self.lock = threading.Lock()
        self.halted = threading.Event()
        self.ceiling = ceiling
        self.liability = 0.0
        for p in root.glob("panel/*/*/*/batches/*/request_started.json"):
            started = read(p)
            response = p.parent / "response.json"
            info = read(response) if response.exists() else None
            self.liability += (
                info["estimated_usd"]
                if info and not info["usage_unknown"]
                else started["reservation_usd"]
            )

    def call(self, directory, arm, contents, schema, identity):
        from google.genai.errors import APIError
        from httpx import TransportError

        response = directory / "response.json"
        if response.exists():
            info = read(response)
            if info["identity"] != identity:
                raise ValueError("saved response identity differs")
            return info
        with self.lock:
            if self.halted.is_set():
                raise RuntimeError("stage halted after an infrastructure failure")
            marker = directory / "request_started.json"
            if marker.exists():
                raise RuntimeError(f"unresolved request, refusing resample: {marker}")
            reservation = cost(arm, 200000, settings(arm)["max_output_tokens"])
            if self.liability + reservation > self.ceiling:
                raise RuntimeError("study cost ceiling reached; no replacement or extra call")
            write(
                marker,
                {
                    "identity": identity,
                    "reservation_usd": reservation,
                    "started_unix": time.time(),
                },
            )
            self.liability += reservation
            started = time.monotonic()
            try:
                info = generate(os.environ["AGCWS_GCP_PROJECT"], arm, contents, schema)
            except (APIError, TransportError) as exc:
                info = {
                    "raw_text": "",
                    "tokens_in": None,
                    "tokens_out": None,
                    "thinking_tokens": None,
                    "estimated_usd": None,
                    "usage_unknown": True,
                    "model_version": None,
                    "finish_reasons": [],
                    "prompt_feedback": None,
                    "api_error": {"type": type(exc).__name__, "message": str(exc)},
                }
            info.update(identity=identity, request_wall_clock_s=time.monotonic() - started)
            write(response, info)
            if not info["usage_unknown"]:
                self.liability += info["estimated_usd"] - reservation
            return info
