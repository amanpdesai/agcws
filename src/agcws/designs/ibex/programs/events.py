"""Operand facts from executed retirement records, not model-intended operands."""

import re

READ = re.compile(r"\bx(\d+):0x([0-9a-fA-F]{8})\b")


def event(line):
    fields = line.split()
    if len(fields) < 4:
        raise ValueError("malformed retirement record")
    tick, cycle, pc, word = (
        int(fields[0]),
        int(fields[1]),
        int(fields[2], 16),
        int(fields[3], 16),
    )
    if word & 3 != 3:
        raise ValueError("compressed instruction in RV32IM observation")
    values = {0: 0}
    for register, value in READ.findall(line):
        register, value = int(register), int(value, 16)
        if register in values and values[register] != value:
            raise ValueError("conflicting source-register values")
        values[register] = value
    opcode, funct3, funct7 = word & 127, (word >> 12) & 7, word >> 25
    result = {"tick": tick, "cycle": cycle, "pc": pc, "kind": "other"}
    if (opcode, funct3, funct7) == (0x33, 5, 1) or opcode == 0x63:
        rs1, rs2 = (word >> 15) & 31, (word >> 20) & 31
        if rs1 not in values or rs2 not in values:
            raise ValueError("missing executed operand values")
        a, b = values[rs1], values[rs2]
        if opcode == 0x33:
            result.update(kind="divide", numerator_zero=a == 0, divisor_zero=b == 0)
        else:

            def signed(x):
                return x if x < 2**31 else x - 2**32

            comparisons = {
                0: a == b,
                1: a != b,
                4: signed(a) < signed(b),
                5: signed(a) >= signed(b),
                6: a < b,
                7: a >= b,
            }
            if funct3 not in comparisons:
                raise ValueError("illegal branch encoding")
            result.update(kind="branch", taken_from_operands=comparisons[funct3])
    return result


def extract(lines, begin, end, phase_map):
    if end - begin != 400000:
        raise ValueError("fixed observation required")
    bins = [
        {
            "divide_zero_divisor": 0,
            "divide_nonzero_divisor": 0,
            "divide_zero_numerator": 0,
            "branch_taken_from_operands": 0,
            "branch_not_taken_from_operands": 0,
            "retired_by_phase": {},
        }
        for _ in range(8)
    ]
    bounds, previous, seen_before, seen_after = {}, None, False, False
    for line in lines:
        tick = int(line.split()[0])
        seen_before |= tick <= begin
        seen_after |= tick >= end
        if not begin <= tick < end:
            continue
        item = event(line)
        if previous is not None and (
            item["cycle"] <= previous["cycle"]
            or item["tick"] - previous["tick"] != 2 * (item["cycle"] - previous["cycle"])
        ):
            raise ValueError("retirement clock mapping changed")
        previous = item
        phases = [p["phase"] for p in phase_map if p["begin_pc"] <= item["pc"] < p["end_pc"]]
        if len(phases) != 1:
            raise ValueError("unmapped or ambiguous executed phase")
        phase = phases[0]
        record = bounds.setdefault(
            phase,
            {
                "first_retired_cycle": (tick - begin) // 2,
                "last_retired_cycle": (tick - begin) // 2,
                "retired": 0,
            },
        )
        record["last_retired_cycle"] = (tick - begin) // 2
        record["retired"] += 1
        window = bins[(tick - begin) // 50000]
        window["retired_by_phase"][phase] = window["retired_by_phase"].get(phase, 0) + 1
        if item["kind"] == "divide":
            window["divide_zero_divisor" if item["divisor_zero"] else "divide_nonzero_divisor"] += 1
            window["divide_zero_numerator"] += item["numerator_zero"]
        elif item["kind"] == "branch":
            window[
                "branch_taken_from_operands"
                if item["taken_from_operands"]
                else "branch_not_taken_from_operands"
            ] += 1
    if not seen_before or not seen_after:
        raise ValueError("trace does not cover observation")
    return {
        "begin_tick": begin,
        "end_tick": end,
        "bins": bins,
        "phases": bounds,
        "scope": "retired PCs and source operand values; phase bounds are retirement times, not issue times or attributed stall cycles",
    }
