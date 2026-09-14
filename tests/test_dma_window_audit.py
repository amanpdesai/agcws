import runpy

import pytest

timing = runpy.run_path("analysis/dma_window_audit.py")["timing"]


def observed():
    return {"read_descriptors": 64, "write_completions": 64, "useful_work_bytes": 4096,
            "observation_cycles": 12000, "padded_until_ns": 120005,
            "completion_ns": 76580, "declared_schedule_end_ns": 76595,
            "trailing_idle_cycles": 0}


def test_padding_uses_dma_own_record_and_clock_units():
    result = timing(observed())
    assert result == {"completion_cycles": 7658, "schedule_end_cycles": 7659.5,
                      "padding_cycles": 4340.5}


@pytest.mark.parametrize("field,value", [("useful_work_bytes", 64),
                                         ("completion_ns", 130000),
                                         ("trailing_idle_cycles", 1000),
                                         ("observation_cycles", 8000)])
def test_inconsistent_records_rejected(field, value):
    record = observed()
    record[field] = value
    with pytest.raises(ValueError):
        timing(record)


def test_new_window_requires_its_own_duration_and_padding():
    record = observed()
    record.update(observation_cycles=9216, padded_until_ns=92165)
    assert timing(record, 9216)["padding_cycles"] == 1556.5
    with pytest.raises(ValueError):
        timing(record)
