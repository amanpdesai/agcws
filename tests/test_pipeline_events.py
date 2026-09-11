import random

import pytest

from agcws.pipeline.ibex.compiler import assembly, phases
from agcws.pipeline.ibex.compiler import unannotated_assembly as original
from agcws.pipeline.ibex.events import event, extract
from agcws.pipeline.ibex.program import random_program


@pytest.mark.parametrize("seed", range(10))
def test_labels_do_not_change_any_original_assembly_line(seed):
    p = random_program(random.Random(seed))
    lines = [
        line
        for line in assembly(p).splitlines()
        if not line.startswith((".global agcws_", "agcws_"))
    ]
    assert "\n".join(lines) + "\n" == original(p)


def divline(tick, a=0, b=1):
    word = (1 << 25) | (11 << 20) | (10 << 15) | (5 << 12) | (10 << 7) | 0x33
    return f"{tick} {tick // 2} 1000 {word:08x} divu x10,x10,x11 x10:0x{a:08x} x11:0x{b:08x} x10=0x00000000"


def test_zero_numerator_is_not_zero_divisor_and_writes_are_not_reads():
    x = event(divline(10))
    assert x["numerator_zero"] and not x["divisor_zero"]
    assert event(divline(10, 1, 0))["divisor_zero"]
    with pytest.raises(ValueError, match="missing executed"):
        event(divline(10).replace("x11:0x00000001", ""))


def test_fixed_window_operand_counts_and_phase_retirement_times():
    mapping = [{"begin_pc": 0x1000, "end_pc": 0x1100, "phase": "segment_0_body"}]
    x = extract(
        [divline(8), divline(10), divline(50010, 1, 0), divline(400010)],
        10,
        400010,
        mapping,
    )
    assert x["bins"][0]["divide_zero_numerator"] == 1
    assert x["bins"][0]["divide_nonzero_divisor"] == 1
    assert x["bins"][1]["divide_zero_divisor"] == 1
    assert x["phases"]["segment_0_body"]["last_retired_cycle"] == 25000
    with pytest.raises(ValueError, match="unmapped"):
        extract([divline(10), divline(400010)], 10, 400010, [])


def test_phase_addresses_reject_overlap():
    with pytest.raises(ValueError, match="strictly"):
        phases({"measure_start": 10, "body_complete": 10, "measure_stop": 20}, 0)
