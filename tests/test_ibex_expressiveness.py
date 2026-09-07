import json
import random

import pytest

from experiments.ibex_temporal_v1 import search as search_module
from experiments.ibex_temporal_v2 import search as search_v2


@pytest.mark.parametrize("module", [search_module, search_v2])
def test_search_charges_short_batches_and_right_censors(tmp_path, monkeypatch, module):
    class FakeAgent:
        def __init__(self):
            self.last_usage = {"tokens_in": 3, "tokens_out": 5}
            self.last_diagnostics = {}

        @classmethod
        def from_vertex(cls, *args, **kwargs):
            return cls()

        def propose(self, *args):
            return [{}]

    manifest = {
        "sources": {},
        "targets": {"t": {"rates": [1] * 8}},
        "seeds": [600],
        "policies": ["agent"],
        "scale": 1,
        "tolerance": 0.1,
        "budget": 4,
        "model": "fake",
        "input_rate": 0.3,
        "output_rate": 2.5,
        "measurement_fingerprint": "test",
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(module, "ProgramAgent", FakeAgent)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test")
    monkeypatch.setattr(
        module,
        "measured",
        lambda *args: ({"valid": False, "stage": "SCHEMA", "reason": "test"}, False),
    )
    module.search(path, tmp_path, "t", "agent", 600)
    output = tmp_path / "panel/t/seed-600/agent"
    summary = json.loads((output / "summary.json").read_text())
    trials = [
        json.loads(line) for line in (output / "trials.jsonl").read_text().splitlines()
    ]
    assert len(trials) == 4 and summary["auc"] == 3
    assert summary["right_censored"] and summary["evaluations_to_target"] == 4
    assert sum(t["tokens_in"] for t in trials) == 3
    assert sum(t["tokens_out"] for t in trials) == 5


def test_error_requires_matching_eight_bin_profiles():
    assert search_module.error([1] * 8, [0] * 8, 2) == 0.5
    with pytest.raises(ValueError):
        search_module.error([1], [0] * 8, 2)


from experiments.ibex_temporal_v1 import activity
from experiments.ibex_temporal_v1.program import (
    MASK,
    WORK,
    assembly,
    interpret,
    mutate,
    random_program,
    validate,
)


def single(op):
    return {
        "registers": [0, 17, MASK, 3, 4, 5, 6, 7],
        "memory_seed": 123,
        "segments": [{"iterations": WORK, "release": 0, "body": [op]}],
    }


def test_interpreter_division_and_overflow():
    zero = single({"op": "divu", "dst": 2, "a": 2, "b": 0})
    assert interpret(zero)["registers"][2] == MASK
    normal = single({"op": "divu", "dst": 2, "a": 2, "b": 1})
    assert interpret(normal)["registers"][2] == 0
    add = single({"op": "add", "dst": 2, "a": 2, "b": 1})
    assert interpret(add)["registers"][2] == (MASK + 17 * WORK) & MASK


def test_memory_and_conditional_reference():
    store = single({"op": "store", "a": 1, "b": 2})
    assert interpret(store)["memory"][17] == MASK
    for source, expected in [(0, 17), (3, MASK)]:
        conditional = single({"op": "cmovz", "dst": 2, "a": source, "b": 1})
        assert interpret(conditional)["registers"][2] == expected


def test_emits_real_loop_not_unrolled_program():
    text = assembly(single({"op": "mul", "dst": 2, "a": 2, "b": 1}))
    assert text.count("  mul ") == 1
    assert "bnez t6, .Lloop0" in text
    assert "measure_start:" in text and "measure_stop:" in text


def test_random_and_mutation_preserve_work():
    rng = random.Random(99)
    for _ in range(30):
        program = random_program(rng)
        validate(program)
        validate(mutate(program, rng))
    program["segments"][0]["iterations"] += 1
    with pytest.raises(ValueError):
        validate(program)


def waveform(unknown=False):
    yield "$timescale 1ps $end\n"
    yield "$scope module TOP $end\n"
    yield "$scope module ibex_simple_system $end\n"
    yield "$scope module u_top $end\n"
    yield "$var wire 1 c clk_i $end\n"
    yield "$scope module u_ibex_top $end\n"
    yield "$scope module u_ibex_core $end\n"
    yield "$var wire 4 d data $end\n"
    yield "$var wire 4 d alias $end\n"
    yield "$enddefinitions $end\n"
    yield "#0\n"
    yield "0c\n"
    yield "bxxxx d\n" if unknown else "b0000 d\n"
    for tick in range(1, 21):
        yield f"#{tick}\n"
        yield f"{1 if tick % 2 == 0 else 0}c\n"
        if tick in (2, 18):
            yield "b1111 d\n" if tick == 2 else "b0000 d\n"


def test_stream_counts_bits_once_and_excludes_end(monkeypatch):
    monkeypatch.setattr(activity, "HORIZON", 8)
    result = activity.stream_activity(waveform(), 2, 18)
    assert result["selected_identifiers"] == 1
    assert result["window_bit_transitions"] == [4, 0, 0, 0, 0, 0, 0, 0]
    assert result["clock_edges"] == 8


def test_stream_rejects_unknown_carried_state(monkeypatch):
    monkeypatch.setattr(activity, "HORIZON", 8)
    with pytest.raises(ValueError, match="carried state"):
        activity.stream_activity(waveform(unknown=True), 2, 18)
