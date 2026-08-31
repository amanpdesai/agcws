from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

class ValidityStage(Enum):
    SCHEMA = "SCHEMA"
    PROTOCOL = "PROTOCOL"
    FUNCTIONAL = "FUNCTIONAL"
    USEFUL_WORK = "USEFUL_WORK"

@dataclass(frozen=True)
class Validity:
    valid: bool
    stage: ValidityStage | None = None
    reason: str | None = None

@dataclass(frozen=True)
class SimResult:
    terminated: bool
    assertions_ok: bool
    outputs_ok: bool
    useful_work: float
    raw: Any = None

class DesignAdapter(ABC):
    name: str
    workload_schema: dict
    regions: list[str] | None = None
    useful_work_floor: float = 0.0
    # Optional activity-level attribution rules.  These are not gate-level
    # power partitions; evaluators must preserve that fidelity distinction.
    activity_region_prefixes: dict[str, tuple[str, ...]] | None = None

    @abstractmethod
    def validate_schema(self, workload: dict) -> Validity: ...
    @abstractmethod
    def validate_protocol(self, workload: dict) -> Validity: ...
    @abstractmethod
    def elaborate(self, workload: dict) -> Any: ...
    @abstractmethod
    def useful_work(self, result: SimResult) -> float: ...

    def validate_result(self, result: SimResult) -> Validity:
        if not result.terminated or not result.assertions_ok or not result.outputs_ok:
            return Validity(False, ValidityStage.FUNCTIONAL, "simulation did not complete legally")
        if result.useful_work < self.useful_work_floor:
            return Validity(False, ValidityStage.USEFUL_WORK, f"useful work {result.useful_work} < floor {self.useful_work_floor}")
        return Validity(True)
