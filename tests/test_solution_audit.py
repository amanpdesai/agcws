import json

import pytest

from analysis.solution_audit import select, trials
from analysis.solution_trace_audit import grids, stream
from analysis.solution_work_audit import changes


def waveform():
    lines = [
        "$scope module top $end",
        "$var wire 1 ! clk $end",
        "$var wire 2 a data $end",
        "$var wire 2 a alias $end",
        "$scope module cs_registers_i $end",
        "$var wire 1 b excluded $end",
        "$upscope $end",
        "$upscope $end",
        "$enddefinitions $end",
        "#0",
        "0!",
        "b00 a",
        "0b",
    ]
    for i in range(32):
        lines += [
            f"#{2 + i * 2}",
            "1!",
            f"b{'11' if i % 2 == 0 else '00'} a",
            f"{i % 2}b",
            f"#{3 + i * 2}",
            "0!",
        ]
    return lines + ["#66", "b11 a"]


def test_independent_counter_alias_exclusion_and_half_open_window():
    counts, edges = stream(waveform(), 2, 66, "top", "top.clk")
    assert counts == [2] * 32
    assert edges == [1] * 32
    for grid in grids(counts, edges).values():
        assert sum(grid["cycles"]) == 32
        assert sum(a * b for a, b in zip(grid["rates"], grid["cycles"])) == 64


def test_unknown_carried_state_rejected():
    lines = waveform()
    lines[lines.index("b00 a")] = "bxx a"
    with pytest.raises(ValueError, match="unknown carried state"):
        stream(lines, 2, 66, "top", "top.clk")


def test_architectural_no_change_is_separate_from_operation_count():
    program = {
        "registers": [0, 1, 0xFFFFFFFF, 0, 0, 0, 0, 0],
        "memory_seed": 0,
        "segments": [
            {
                "body": [
                    {"op": "add", "a": 0, "b": 0, "dst": 0},
                    {"op": "add", "a": 2, "b": 1, "dst": 3},
                    {"op": "divu", "a": 1, "b": 0, "dst": 4},
                    {"op": "store", "a": 0, "b": 0},
                ]
            }
        ],
    }
    result = changes(program, [4])
    assert result["registers"][3:5] == [0, 0xFFFFFFFF]
    assert sum(result["operations"].values()) == 4
    assert result["unchanged_fraction"] == 0.75


def test_selector_ties_unsolved_and_first_invalid(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"seeds": [1], "tolerance": 0.1}))
    cell = {"target": "t", "seed": 1, "arm": "a"}
    (tmp_path / "search_manifest.json").write_text(json.dumps({"cells": [cell]}))
    directory = tmp_path / "panel/t/1/a/batches/001"
    directory.mkdir(parents=True)
    import gzip

    rows = [{"slot": i, "valid": i != 2, "loss": 0.2 if i < 100 else 0.8} for i in range(1, 129)]
    (directory / "trials.json.gz").write_bytes(gzip.compress(json.dumps(rows).encode()))
    assert select(tmp_path)["cells"][0]["roles"] == {
        "first_solve": None,
        "best": 1,
        "worst_valid": 100,
        "first_invalid": 2,
    }
    (directory / "trials.json.gz").write_bytes(gzip.compress(json.dumps(rows[:-1]).encode()))
    with pytest.raises(ValueError, match="incomplete"):
        trials(tmp_path, cell)
