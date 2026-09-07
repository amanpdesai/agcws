import copy
import json
import random

import jsonschema
import pytest

from experiments.ibex_temporal_v2 import program as v2
from experiments.ibex_temporal_v2.compiler import assembly as old_assembly
from experiments.ibex_temporal_v3 import program
from experiments.ibex_temporal_v3.feedback import instruction_class, retirement_bins
from experiments.ibex_temporal_v3.coverage import BehaviorArchive, descriptor
from experiments.ibex_temporal_v3.agent import TemporalAgent, prompt


def test_integral_encodings_preserve_program_state_and_machine_source():
    for seed in range(20):
        original = v2.random_program(random.Random(seed))
        floating = json.loads(json.dumps(original), parse_int=float)
        snapshot = copy.deepcopy(floating)
        assert program.canonical(floating) == original
        assert program.interpret(floating) == v2.interpret(original)
        assert program.assembly(floating) == old_assembly(original)
        assert floating == snapshot


@pytest.mark.parametrize(
    "value", [True, 1.5, float("inf"), float("nan"), "1", -1, 4097]
)
def test_numeric_fix_does_not_repair_invalid_weights(value):
    item = program.random_program(random.Random(1))
    item["segments"][0]["weight"] = value
    with pytest.raises(jsonschema.ValidationError):
        program.canonical(item)


@pytest.mark.parametrize(
    "word,category",
    [
        (0x02000033, "multiply"),
        (0x02003033, "multiply"),
        (0x02004033, "divide"),
        (0x02007033, "divide"),
        (0x00000003, "load"),
        (0x00000023, "store"),
        (0x00000063, "branch"),
        (0x0000006F, "jump"),
        (0x00000067, "jump"),
        (0xB0002073, "csr"),
        (0x00000013, "alu"),
        (0x00000073, "other"),
    ],
)
def test_instruction_classes(word, category):
    assert instruction_class(word) == category


def line(tick, instruction="00000013"):
    return f"{tick} {tick // 2} 00100100 {instruction} ignored operands\n"


def test_temporal_feedback_uses_same_half_open_interval():
    lines = [
        line(8),
        line(10),
        line(50008, "02004033"),
        line(50010, "00000003"),
        line(400010, "00000023"),
    ]
    result = retirement_bins(lines, 10, 400010)
    assert result["retired_per_bin"] == [2, 1, 0, 0, 0, 0, 0, 0]
    assert result["retired_classes"][0]["divide"] == 1
    assert result["retired_classes"][1]["load"] == 1
    assert sum(c["store"] for c in result["retired_classes"]) == 0
    assert sum(result["cycles_without_retirement"]) == 200000 - 3


def test_feedback_rejects_truncated_or_misaligned_traces():
    for lines in ([], [line(10)], [line(12), line(400010)]):
        with pytest.raises(ValueError, match="cover"):
            retirement_bins(lines, 10, 400010)
    with pytest.raises(ValueError, match="clock mapping"):
        retirement_bins([line(10), "12 9 00100100 00000013"], 10, 400010)
    with pytest.raises(ValueError, match="compressed"):
        instruction_class(1)


def test_behavior_archive_is_measured_and_retains_best_in_each_cell():
    feedback = retirement_bins([line(10), line(400010)], 10, 400010)
    archive = BehaviorArchive()
    trial = {
        "slot": 1,
        "valid": True,
        "loss": 0.5,
        "feedback": feedback,
        "program": program.random_program(random.Random(4)),
    }
    assert archive.observe(trial)
    assert not archive.observe({**trial, "slot": 2, "loss": 0.9})
    assert archive.representatives()[0]["slot"] == 1
    assert not archive.observe({**trial, "slot": 3, "loss": 0.2})
    assert archive.representatives()[0]["slot"] == 3
    changed = copy.deepcopy(feedback)
    changed["cycles_without_retirement"][0] = 0
    assert descriptor(changed) != descriptor(feedback)
    assert archive.observe({**trial, "slot": 4, "feedback": changed})
    assert not archive.observe({"valid": False})
    assert len(archive.elites) == 2
    candidate, record = archive.propose(random.Random(10))
    program.validate(candidate)
    assert record["mode"] == "archive-guided-mutation"
    assert record["parent_slot"] in (3, 4)


def test_coverage_mutations_explore_structure_without_losing_work():
    rng = random.Random(62)
    item = program.random_program(rng)
    lengths = set()
    for _ in range(200):
        before = copy.deepcopy(item)
        child = program.mutate(item, rng)
        assert item == before
        assert sum(program.allocation(child)) == 4096
        lengths.update(len(s["body"]) for s in child["segments"])
        item = child
    assert {3, 5, 6, 7} <= lengths


@pytest.mark.parametrize(
    "source,correction", [(False, False), (True, False), (False, True), (True, True)]
)
def test_context_and_correction_treatments_are_separate(source, correction):
    agent = TemporalAgent(lambda *_: "{}", prompt(source, correction), model="fake")
    agent.source_context = {"excerpts": ["allowlisted RTL"]} if source else None
    agent.correction = correction
    row = {
        "slot": 1,
        "program": program.random_program(random.Random(4)),
        "valid": True,
        "reason": "",
        "loss": 0.4,
        "rates": [1] * 8,
        "residual": [-0.2] * 8,
        "allocation": [4096],
        "feedback": retirement_bins([line(10), line(400010)], 10, 400010),
        "tokens_in": "DO_NOT_SEND",
        "hidden_witness": "DO_NOT_SEND",
    }
    raw = agent.build_payload(None, {}, [row], 2, agent.system_prompt)
    payload = json.loads(raw)
    assert ("source_context" in payload) == source
    assert ("feedback" in payload["history"][0]) == correction
    assert ("behavior_cells_seen" in payload) == correction
    assert "DO_NOT_SEND" not in raw
    if correction:
        assert payload["reference_slot"] == 1
