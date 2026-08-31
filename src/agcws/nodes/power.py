from dataclasses import dataclass
from typing import Literal
import re
from pathlib import Path

@dataclass(frozen=True)
class PowerProfile:
    mean_power: float
    peak_power: float
    windowed: list[float] | None = None
    by_region: dict[str, float] | None = None
    useful_work: float = 0.0
    valid: bool = False
    fidelity: Literal["activity", "synthesis"] = "activity"
    provenance: dict[str, str] | None = None
    per_cycle_toggles: list[int] | None = None


_POWER_LINE = re.compile(
    r"(?im)^\s*(?P<label>total|internal|switching|leakage)\s+power\s*"
    r"(?:=|:)\s*(?P<value>[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)"
)
_POWER_TABLE_TOTAL = re.compile(
    r"(?im)^\s*Total\s+"
    r"(?P<internal>[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s+"
    r"(?P<switching>[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s+"
    r"(?P<leakage>[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s+"
    r"(?P<total>[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s+100\.0%"
)


def parse_opensta_power_report(report: str, *, provenance: dict[str, str] | None = None) -> PowerProfile:
    """Parse the strict scalar power fields emitted by an OpenSTA report.

    A total is mandatory; silently turning an unrecognized report into zero is
    forbidden because that would create a valid-looking fake measurement.
    """
    values = {match.group("label").lower(): float(match.group("value"))
              for match in _POWER_LINE.finditer(report)}
    table = _POWER_TABLE_TOTAL.search(report)
    if "total" not in values and table:
        values = {name: float(table.group(name)) for name in
                  ("internal", "switching", "leakage", "total")}
    if "total" not in values:
        raise ValueError("OpenSTA report has no parseable Total Power field")
    return PowerProfile(
        mean_power=values["total"],
        peak_power=values["total"],
        useful_work=0.0,
        valid=True,
        fidelity="synthesis",
        provenance=provenance,
    )


def parse_opensta_power_file(path: Path, *, provenance: dict[str, str] | None = None) -> PowerProfile:
    return parse_opensta_power_report(path.read_text(), provenance=provenance)
