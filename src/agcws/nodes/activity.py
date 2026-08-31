from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence
from collections import defaultdict
from bisect import bisect_right
import json
import re
from agcws.nodes.commands import CommandResult, run_command

_VAR_RE = re.compile(r"\$var\s+\S+\s+(\d+)\s+(\S+)\s+(.+?)\s+\$end")

@dataclass(frozen=True)
class ActivityArtifact:
    activity_file: Path
    annotation_fraction: float | None = None
    per_cycle_toggles: tuple[int, ...] = ()
    window_toggles: tuple[int, ...] = ()

def windowize(values: Sequence[int], windows: int) -> tuple[int, ...]:
    """Aggregate per-cycle toggles into deterministic coarse windows."""
    if windows <= 0 or not values:
        raise ValueError("windows must be positive and values must be non-empty")
    buckets = [0] * min(windows, len(values))
    for index, value in enumerate(values):
        buckets[index * len(buckets) // len(values)] += value
    return tuple(buckets)


def attribute_regions(signal_transitions: dict[str, int],
                      region_prefixes: dict[str, tuple[str, ...]]) -> dict[str, float]:
    """Aggregate signal transitions into declared RTL regions.

    This is an activity-fidelity attribution, not a claim of gate-level power
    partitioning. Prefix rules are explicit adapter metadata so unmatched
    signals remain visible instead of silently disappearing.
    """
    totals = {region: 0.0 for region in region_prefixes}
    totals["unattributed"] = 0.0
    for signal, count in signal_transitions.items():
        matches = [region for region, prefixes in region_prefixes.items()
                   if any(signal.startswith(prefix) for prefix in prefixes)]
        region = matches[0] if len(matches) == 1 else "unattributed"
        totals[region] += float(count)
    return totals


def parse_vcd(path: Path, clock_name: str = "clk_i", windows: int = 16) -> dict:
    """Extract deterministic transition counts without invoking EDA tools."""
    if windows <= 0:
        raise ValueError("windows must be positive")
    identifiers: dict[str, tuple[str, int]] = {}
    clocks: set[str] = set()
    values: dict[str, str] = {}
    transitions: defaultdict[str, int] = defaultdict(int)
    per_time: defaultdict[int, int] = defaultdict(int)
    edges: list[int] = []
    time, header = 0, True
    for line in path.read_text(errors="replace").splitlines():
        match = _VAR_RE.search(line) if header else None
        if match:
            width, identifier, name = int(match[1]), match[2], match[3]
            identifiers[identifier] = (name, width)
            if name.split()[-1] == clock_name:
                clocks.add(identifier)
            continue
        if line.startswith("$enddefinitions"):
            header = False
        elif line.startswith("#"):
            time = int(line[1:])
        elif line and line[0] not in "$ ":
            if line[0] in "01xXzZ":
                value, identifier = line[0], line[1:]
            elif line[0] == "b":
                value, identifier = line.split(maxsplit=1)
            else:
                continue
            old = values.get(identifier)
            if old is not None and old != value:
                name = identifiers.get(identifier, (identifier, 1))[0]
                transitions[name] += 1
                per_time[time] += 1
            values[identifier] = value
            if identifier in clocks and old == "0" and value == "1":
                edges.append(time)
    edges.sort()
    if not edges:
        edges = sorted(per_time)
    per_cycle = [0] * len(edges)
    for timestamp, count in per_time.items():
        cycle = bisect_right(edges, timestamp) - 1
        if cycle >= 0:
            per_cycle[cycle] += count
    bucket_count = min(windows, max(1, len(edges)))
    buckets = [0] * bucket_count
    for timestamp, count in per_time.items():
        cycle = bisect_right(edges, timestamp) - 1
        if cycle >= 0:
            buckets[min(cycle * bucket_count // max(1, len(edges)), bucket_count - 1)] += count
    return {"vcd": path.name, "clock": clock_name, "clock_edges": len(edges),
            "total_transitions": sum(transitions.values()),
            "signal_transitions": dict(sorted(transitions.items())),
            "per_cycle_toggles": per_cycle, "window_toggles": buckets}

def extract_activity(command: list[str], waveform: Path, output_dir: Path, *, clock_name: str = "clk_i", windows: int = 16) -> tuple[CommandResult, ActivityArtifact]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(command, cwd=output_dir)
    if not waveform.is_file():
        raise FileNotFoundError(f"activity command did not produce waveform: {waveform}")
    activity = parse_vcd(waveform, clock_name, windows)
    (output_dir / "activity.json").write_text(json.dumps(activity, indent=2, sort_keys=True) + "\n")
    return result, ActivityArtifact(output_dir / "activity.saif",
                                   per_cycle_toggles=tuple(activity["per_cycle_toggles"]),
                                   window_toggles=tuple(activity["window_toggles"]))
