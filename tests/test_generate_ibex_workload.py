import json

from scripts.generate_ibex_workload import generate


def test_generated_ibex_workload_is_deterministic_and_floor_compliant():
    workload = generate(10_000)
    assert len(workload["program"]) == 10_001
    assert workload["program"][-1] == {"op": "ecall"}
    assert all(item == {"op": "nop"} for item in workload["program"][:-1])
    assert json.dumps(workload, sort_keys=True) == json.dumps(generate(10_000), sort_keys=True)
