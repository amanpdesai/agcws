"""Explicit study configuration; prepare never starts measurements or model calls."""

import math
from pathlib import Path

from agcws.pipeline.backends import backend
from agcws.pipeline.model import MODELS
from agcws.pipeline.policies.controls import ARMS


def validate(spec):
    required = {
        "name",
        "domain",
        "targets",
        "seeds",
        "policies",
        "budget",
        "batch_size",
        "scale",
        "tolerance",
        "binary",
        "image",
        "max_workers",
        "cost_ceiling_usd",
    }
    if set(spec) - {"stop_on_success", "provider_workers"} != required:
        raise ValueError(f"exact study fields required: {sorted(required)}")
    if "stop_on_success" in spec and type(spec["stop_on_success"]) is not bool:
        raise ValueError("stop_on_success must be boolean")
    if "provider_workers" in spec and (
        type(spec["provider_workers"]) is not int or spec["provider_workers"] < 1
    ):
        raise ValueError("positive integer provider_workers required")
    design = backend(spec["domain"])
    if not spec["name"] or not isinstance(spec["name"], str):
        raise ValueError("study name required")
    for field in ("budget", "batch_size", "max_workers"):
        if type(spec[field]) is not int or spec[field] < 1:
            raise ValueError(f"positive integer {field} required")
    if spec["budget"] % spec["batch_size"]:
        raise ValueError("budget must be divisible by batch size")
    if spec["budget"] < 2:
        raise ValueError("AUC requires at least two proposal slots")
    for field in ("binary", "image"):
        if field == "binary" and design.binary_path is None:
            if spec[field] is not None:
                raise ValueError("source-built backend requires binary=null")
            continue
        if not isinstance(spec[field], str) or not spec[field].strip():
            raise ValueError(f"explicit {field} required")
    for field in ("scale", "tolerance", "cost_ceiling_usd"):
        if (
            type(spec[field]) not in (int, float)
            or not math.isfinite(spec[field])
            or spec[field] <= 0
        ):
            raise ValueError(f"positive finite {field} required")
    for field in ("seeds", "policies"):
        if not spec[field] or len(set(spec[field])) != len(spec[field]):
            raise ValueError(f"nonempty unique {field} required")
    if any(type(seed) is not int or seed < 0 for seed in spec["seeds"]):
        raise ValueError("nonnegative integer seeds required")
    if any(arm not in (*ARMS, *MODELS) for arm in spec["policies"]):
        raise ValueError("unknown policy")
    if hasattr(design, "allowed_policies") and any(
        arm not in design.allowed_policies for arm in spec["policies"]
    ):
        raise ValueError("policy is not implemented for this backend")
    if any(a.startswith("gest-") or a == "ridge-screen" for a in spec["policies"]) and (
        spec["budget"] < 8 or spec["budget"] % 4 or spec["batch_size"] != 4
    ):
        raise ValueError(
            "GeST/screening panels require batch_size=4 and budget multiple of four >=8; gest-batch2 is the explicit feedback-frequency control"
        )
    if not isinstance(spec["targets"], dict) or not spec["targets"]:
        raise ValueError("named target vectors required")
    for name, rates in spec["targets"].items():
        if not name or Path(name).name != name or name in (".", ".."):
            raise ValueError("target name must be a single safe path component")
        if len(rates) != 8 or any(
            type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in rates
        ):
            raise ValueError("eight nonnegative finite target rates required")
    return spec
