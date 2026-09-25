"""Versioned transport recovery; never convert infrastructure errors to proposals."""

import fcntl
import os
import random
import threading
import time
from email.utils import parsedate_to_datetime

from google.genai.errors import APIError
from httpx import TransportError

from agcws.core.storage import ensure, read, write
from agcws.search.providers.gemini import cost, generate, settings
from agcws.search.providers.schema import provenance

VERSION = "provider-recovery-v1"
MAX_ATTEMPTS = 4


class InfrastructurePause(RuntimeError):
    pass


def error_record(exc):
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", {}) or {}
    return {
        "type": type(exc).__name__, "message": str(exc),
        "code": getattr(exc, "code", None), "status": getattr(exc, "status", None),
        "details": getattr(exc, "details", None),
        "headers": {k: headers[k] for k in
                    ("retry-after", "x-request-id", "x-goog-request-id") if k in headers},
    }


class RecoveryMeter:
    """Serial provider admission, durable attempts and a cross-design pause file.

    Only explicit transient HTTP failures are retried. Ambiguous transport loss
    pauses immediately. Every unsuccessful attempt retains its full cost reserve.
    A returned model response, even invalid JSON, is never retried here.
    """

    def __init__(self, root, ceiling, provider_workers=1):
        if type(provider_workers) is not int or provider_workers < 1:
            raise ValueError("positive integer provider_workers required")
        self.root = root.resolve()
        self.ceiling = ceiling
        self.halted = threading.Event()
        self.pause_path = self.root.parent / "provider-paused.json"
        self.admission_path = self.root.parent / "provider-global.lock"
        self.liability = self._liability()

    def _liability(self):
        total = 0.0
        for marker in self.root.glob("panel/*/*/*/batches/*/attempts/*/request_started.json"):
            info = read(marker.parent / "response.json") if (marker.parent / "response.json").exists() else None
            total += (info["estimated_usd"] if info and not info["usage_unknown"]
                      else read(marker)["reservation_usd"])
        return total

    def _pause(self, reason):
        self.halted.set()
        if not self.pause_path.exists():
            write(self.pause_path, {"version": VERSION, "reason": reason,
                                    "time": time.time(), "design": self.root.name})
        raise InfrastructurePause(reason)

    def call(self, directory, arm, contents, schema, identity):
        with self.admission_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if self.halted.is_set() or self.pause_path.exists():
                raise InfrastructurePause("provider paused; checkpoints retained")
            request = {"identity": identity, "contents": contents, "arm": arm,
                       "schema_provenance": provenance(schema), "version": VERSION}
            ensure(directory / "transport-request.json", request)
            saved = directory / "response.json"
            if saved.exists():
                info = read(saved)
                if info.get("api_error"):
                    raise ValueError("infrastructure failure cannot be a model response")
                if info.get("identity") != identity or info.get("schema_provenance") != provenance(schema):
                    raise ValueError("saved response identity or schema provenance differs")
                return info
            for number in range(1, MAX_ATTEMPTS + 1):
                attempt = directory / "attempts" / f"{number:03}"
                marker = attempt / "request_started.json"
                response = attempt / "response.json"
                if response.exists():
                    info = read(response)
                else:
                    if marker.exists():
                        self._pause(f"unresolved provider request: {marker}")
                    self.liability = self._liability()
                    reserve = cost(arm, 200000, settings(arm)["max_output_tokens"])
                    if self.liability + reserve > self.ceiling:
                        self._pause("local cost ceiling reached")
                    write(marker, {**request, "reservation_usd": reserve,
                                   "started_unix": time.time()})
                    started = time.monotonic()
                    try:
                        info = generate(os.environ["AGCWS_GCP_PROJECT"], arm, contents, schema)
                    except (APIError, TransportError) as exc:
                        info = {"api_error": error_record(exc), "usage_unknown": True,
                                "estimated_usd": None}
                    info.update(identity=identity, schema_provenance=provenance(schema),
                                request_wall_clock_s=time.monotonic() - started)
                    write(response, info)
                self.liability = self._liability()
                error = info.get("api_error")
                if not error:
                    write(saved, info)
                    return info
                code = error.get("code")
                details = str(error.get("details", "")).upper()
                if any(reason in details for reason in
                       ("BILLING_DISABLED", "BILLING_NOT_ACTIVE", "SPEND_CAP_EXCEEDED")):
                    self._pause(f"explicit billing shutdown: {response}")
                if code not in (429, 500, 502, 503, 504):
                    self._pause(f"non-retryable or ambiguous provider failure: {response}")
                if number == MAX_ATTEMPTS:
                    self._pause(f"provider retry limit reached: {response}")
                delay = random.uniform(10 * 2 ** (number - 1), 20 * 2 ** (number - 1))
                retry_after = error.get("headers", {}).get("retry-after")
                if retry_after is not None:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        try:
                            delay = max(delay, parsedate_to_datetime(retry_after).timestamp() - time.time())
                        except (ValueError, TypeError, OverflowError):
                            self._pause("unrecognized Retry-After; manual review required")
                if not (attempt / "retry.json").exists():
                    write(attempt / "retry.json", {"next_attempt": number + 1, "delay_s": delay})
                delay = read(attempt / "retry.json")["delay_s"]
                while delay > 0:
                    if self.halted.is_set() or self.pause_path.exists():
                        raise InfrastructurePause("provider paused during backoff")
                    step = min(delay, 30)
                    time.sleep(step)
                    delay -= step
