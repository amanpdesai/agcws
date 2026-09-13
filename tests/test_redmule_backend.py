import random
import runpy

import jsonschema
import pytest

from agcws.pipeline.backends import backend


def test_complete_schema_and_seeded_classical_contract():
    design = backend("redmule-temporal")
    rng = random.Random(7104)
    history = []
    for slot in range(1, 33):
        program, parents = design.propose_classical("phase-ga", rng, slot, history)
        jsonschema.validate({"hypothesis": "test", "candidates": [program]}, design.schema(1))
        assert all(parent < slot for parent in parents)
        valid = design.adapter().validate_protocol(program).valid
        history.append({"slot": slot, "program": program, "valid": valid, "loss": 1 / slot})
    assert design.random(random.Random(1)) == design.random(random.Random(1))
    with pytest.raises(ValueError, match="unsupported"):
        design.propose_classical("unknown", rng, 1, [])


def test_source_renderer_is_relocatable_but_rejects_outside_paths(tmp_path):
    render = runpy.run_path("scripts/prepare_redmule_dependencies.py")["container_sources"]
    root = tmp_path / "dependency"
    root.mkdir()
    (root / "dut.sv").touch()
    assert render(f"+define+TEST\n{root}/dut.sv\n", root) == "+define+TEST\n/workspace/.dependencies/dut.sv\n"
    (tmp_path / "outside.sv").touch()
    with pytest.raises(ValueError):
        render(str(tmp_path / "outside.sv"), root)


def test_expected_work_failures_are_not_infrastructure_success(tmp_path):
    design = backend("redmule-temporal")
    assert design.failed(tmp_path) is None
    (tmp_path / "driver.log").write_text("REDMULE_USEFUL_WORK below floor")
    failure = design.failed(tmp_path)
    assert not failure["valid"] and failure["stage"] == "USEFUL_WORK"
    (tmp_path / "driver.log").write_text("compiler failed")
    assert design.failed(tmp_path) is None
