"""Requested shapes are not feasible targets until measured evidence qualifies them."""

import argparse
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path

from experiments.ibex_depth_v1.storage import write
from experiments.ibex_temporal_v3.program import canonical

FAMILIES = ("alternating", "random_steps", "ramp", "burst", "flat")


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Request:
    seed: int
    family: str = "random_steps"
    horizon_cycles: int = 200000
    bins: int = 8
    phases: int = 4
    low: float = 0.2
    high: float = 0.8
    scale: float = 528.45376

    def validate(self):
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("nonnegative integer seed required")
        if self.family not in FAMILIES:
            raise ValueError("unknown shape family")
        if any(
            type(n) is not int for n in (self.horizon_cycles, self.bins, self.phases)
        ):
            raise ValueError("integer duration, bin and phase counts required")
        if not 2 <= self.bins <= 1024 or self.horizon_cycles % self.bins:
            raise ValueError("2..1024 equal integer-cycle bins required")
        if self.horizon_cycles < self.bins or not 1 <= self.phases <= self.bins:
            raise ValueError("positive duration and 1..bins phases required")
        if any(
            type(x) not in (int, float) or not math.isfinite(x)
            for x in (self.low, self.high, self.scale)
        ):
            raise ValueError("finite numeric levels and scale required")
        if not 0 <= self.low < self.high <= 1 or self.scale <= 0:
            raise ValueError("0 <= low < high <= 1 and positive scale required")
        if self.family in ("alternating", "random_steps") and self.phases < 2:
            raise ValueError("step families require at least two phases")


def generate(spec):
    spec.validate()
    rng = random.Random(spec.seed)
    cuts = [0, *sorted(rng.sample(range(1, spec.bins), spec.phases - 1)), spec.bins]
    if spec.family == "ramp":
        values = [
            spec.low + (spec.high - spec.low) * i / (spec.bins - 1)
            for i in range(spec.bins)
        ]
    elif spec.family == "flat":
        values = [(spec.low + spec.high) / 2] * spec.bins
    elif spec.family == "burst":
        start = rng.randrange(spec.bins)
        end = rng.randrange(start + 1, spec.bins + 1)
        if start == 0 and end == spec.bins:
            end -= 1
        values = [spec.high if start <= i < end else spec.low for i in range(spec.bins)]
    else:
        levels = []
        for i in range(spec.phases):
            if spec.family == "alternating":
                level = spec.low if i % 2 == 0 else spec.high
            else:
                # Alternating disjoint bands guarantee changes without rejection sampling.
                width = (spec.high - spec.low) / 4
                base = spec.low if i % 2 == 0 else spec.high - width
                level = rng.uniform(base, base + width)
            levels.append(level)
        values = [
            v
            for v, a, b in zip(levels, cuts[:-1], cuts[1:], strict=True)
            for _ in range(b - a)
        ]
    boundaries = [i * (spec.horizon_cycles // spec.bins) for i in range(spec.bins + 1)]
    payload = {
        "version": 1,
        "status": "unqualified-request",
        "spec": asdict(spec),
        "unit": "RTL bit transitions per clock edge",
        "normalization": "fixed reference scale, not an empirical [min,max] envelope",
        "bin_edges_cycles": boundaries,
        "normalized_rates": values,
        "target_rates": [v * spec.scale for v in values],
        "observed_shape": {
            "transitions": sum(a != b for a, b in pairwise(values)),
            "range": max(values) - min(values),
            "total_variation": sum(abs(a - b) for a, b in pairwise(values)),
        },
    }
    return {"id": digest(payload), **payload}


def witnessed_target(program, result, measurement, scale, horizon=200000, bins=8):
    program = canonical(program)
    if type(horizon) is not int or type(bins) is not int or bins < 1 or horizon < bins:
        raise ValueError("positive integer horizon and bin count required")
    if result["valid"] is not True:
        raise ValueError("invalid workload cannot witness a target")
    if not measurement or not math.isfinite(scale) or scale <= 0:
        raise ValueError("measurement fingerprint and positive scale required")
    profile = result["profile"]
    rates = profile["window_rates"]
    counts = profile["window_bit_transitions"]
    if (
        profile["clock_edges"] != horizon
        or horizon % bins
        or len(rates) != bins
        or len(counts) != bins
    ):
        raise ValueError("witness observation window differs")
    if any(type(n) is not int or n < 0 for n in counts) or rates != [
        n / (horizon // bins) for n in counts
    ]:
        raise ValueError("witness rate/count arithmetic differs")
    return {
        "status": "achieved-witness-target",
        "measurement_fingerprint": measurement,
        "horizon_cycles": horizon,
        "bins": bins,
        "scale": scale,
        "target_rates": rates,
        "witness_program_sha256": digest(program),
        "witness_result_sha256": digest(result),
        "witness_cache_id": result["cache_id"],
        "scope": "Witness must pass independent archive/CPU checks; no arbitrary request feasibility implied.",
    }


def match_request(request, target, tolerance):
    spec = Request(**request["spec"])
    if generate(spec) != request:
        raise ValueError("request differs from deterministic specification")
    if target["status"] != "achieved-witness-target":
        raise ValueError("measured witness target required")
    if (spec.horizon_cycles, spec.bins, spec.scale) != (
        target["horizon_cycles"],
        target["bins"],
        target["scale"],
    ):
        raise ValueError("request and measurement units/windows differ")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("finite nonnegative tolerance required")
    rates = target["target_rates"]
    if len(rates) != spec.bins or any(not math.isfinite(v) or v < 0 for v in rates):
        raise ValueError("finite measured rates in every bin required")
    loss = math.sqrt(
        sum(
            ((a - b) / spec.scale) ** 2
            for a, b in zip(rates, request["target_rates"], strict=True)
        )
        / spec.bins
    )
    return {
        "request_id": request["id"],
        "loss": loss,
        "tolerance": tolerance,
        "qualified": loss <= tolerance,
        "witness": target["witness_program_sha256"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--family", choices=FAMILIES, default="random_steps")
    parser.add_argument("--horizon-cycles", type=int, default=200000)
    parser.add_argument("--bins", type=int, default=8)
    parser.add_argument("--phases", type=int, default=4)
    parser.add_argument("--low", type=float, default=0.2)
    parser.add_argument("--high", type=float, default=0.8)
    parser.add_argument("--scale", type=float, default=528.45376)
    args = vars(parser.parse_args())
    out = args.pop("out")
    write(out, generate(Request(**args)))
