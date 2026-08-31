from scripts.compile_ibex_workload import assembly_for


def test_ibex_compiler_emits_deterministic_halt_and_memory_ops():
    workload = {
        "program": [
            {"op": "lw", "address": 0},
            {"op": "sw", "address": 4},
            {"op": "ecall"},
        ]
    }
    first = assembly_for(workload)
    assert first == assembly_for(workload)
    assert "lw t1, 0(t2)" in first
    assert "sw t1, 0(t2)" in first
    assert "li t2, 0x20008" in first
