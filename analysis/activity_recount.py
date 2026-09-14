"""Independent known-bit versus value-event diagnostic for saved VCDs."""

import argparse
import bisect
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def recount(path, scope, clock, *, exclude_clock=False):
    widths, selected, clocks, stack, values, names = {}, set(), set(), [], {}, {}
    unknown_signals = {}
    counts = defaultdict(lambda: [0, 0, 0])
    edges, timestamp, header = [], 0, True
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for raw in stream:
            digest.update(raw)
            line = raw.decode("ascii").strip()
            fields = line.split()
            if not fields:
                continue
            if header:
                if fields[0] == "$scope":
                    stack.append(fields[2])
                elif fields[0] == "$upscope":
                    stack.pop()
                elif fields[0] == "$var":
                    width, identifier = int(fields[2]), fields[3]
                    name = ".".join([*stack, fields[4]])
                    widths[identifier] = width
                    if name.startswith(scope + "."):
                        selected.add(identifier)
                        names.setdefault(identifier, name)
                    if name == clock:
                        clocks.add(identifier)
                elif fields[0] == "$enddefinitions":
                    header = False
                    if exclude_clock:
                        selected -= clocks
                continue
            if line.startswith("#"):
                timestamp = int(line[1:])
                continue
            if line[0] in "01xXzZ":
                value, identifier = line[0], line[1:]
            elif line[0] in "bB":
                value, identifier = fields[0][1:], fields[1]
            else:
                continue
            if identifier not in selected and identifier not in clocks:
                continue
            old = values.get(identifier)
            values[identifier] = value
            if identifier in clocks and old == "0" and value == "1":
                edges.append(timestamp)
            if old is None or old == value or identifier not in selected:
                continue
            counts[timestamp][0] += 1
            if set(old.lower() + value.lower()) - set("01"):
                counts[timestamp][2] += 1
                record = unknown_signals.setdefault(names[identifier], {"count": 0, "first_tick": timestamp,
                                                                        "last_tick": timestamp})
                record["count"] += 1
                record["last_tick"] = timestamp
            else:
                if max(len(old), len(value)) > widths[identifier]:
                    raise ValueError("value exceeds declared width")
                counts[timestamp][1] += (int(old, 2) ^ int(value, 2)).bit_count()
    if len(clocks) != 1 or not selected or not edges or len(set(edges)) != len(edges):
        raise ValueError("one explicit clock and nonempty scope/window required")
    edges.sort()
    cycles = [[0, 0, 0] for _ in edges]
    before = [0, 0, 0]
    for timestamp, values in counts.items():
        index = bisect.bisect_right(edges, timestamp) - 1
        bucket = cycles[index] if index >= 0 else before
        for k, count in enumerate(values):
            bucket[k] += count
    bins = [cycles[i*len(edges)//8:(i+1)*len(edges)//8] for i in range(8)]
    if any(not b for b in bins):
        raise ValueError("at least eight clock edges required")
    return {"waveform_sha256": digest.hexdigest(), "scope": scope, "clock": clock,
            "clock_edges": len(edges), "clock_in_activity_scope": bool(clocks & selected),
            "pre_first_edge_counts": before, "bin_edges": [len(b) for b in bins],
            "columns": ["identifier_changes", "known_bit_flips", "unknown_value_changes"],
            "unknown_signals": unknown_signals,
            "bin_counts": [[sum(c[k] for c in b) for k in range(3)] for b in bins],
            "bin_rates": [[sum(c[k] for c in b)/len(b) for k in range(3)] for b in bins],
            "scope_note": "same rising-edge bins; bit counts are unweighted, not power"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("waveform", type=Path)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--clock", required=True)
    args = parser.parse_args()
    print(json.dumps(recount(args.waveform, args.scope, args.clock), indent=2))
