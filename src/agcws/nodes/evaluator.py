"""Agent-facing evaluation contract.

Policies submit a workload and receive one structured result.  Tool-specific
commands and reports stay behind this boundary; in particular, RTL activity is
never mislabeled as gate-level power.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from agcws.nodes.power import PowerProfile

Fidelity = Literal["rtl_activity", "gate_level"]


@dataclass(frozen=True)
class EvaluationRequest:
    workload: dict
    fidelity: Fidelity = "rtl_activity"
    output_dir: Path | None = None


@dataclass(frozen=True)
class EvaluationResult:
    """Complete result exposed to a policy after one candidate evaluation."""

    workload: dict
    profile: PowerProfile | None
    valid: bool
    fidelity: Fidelity
    failure_stage: str | None = None
    failure_reason: str | None = None
    artifacts: dict[str, str] = field(default_factory=dict)
    provenance: dict[str, str] = field(default_factory=dict)


class Evaluator(Protocol):
    """Stable boundary implemented by RTL-proxy and gate-level evaluators."""

    fidelity: Fidelity

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate one workload without exposing tool-specific details."""

