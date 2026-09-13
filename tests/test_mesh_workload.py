import copy
import runpy

import jsonschema
import pytest

packet_program = runpy.run_path("scripts/run_mesh_workload.py")["packet_program"]


def workload():
    return {"packets": [{"release_cycle": i // 4, "source": i % 4,
                         "destination": 3 - i % 4, "payload": i} for i in range(64)],
            "sink_period": 8, "sink_pause": 3}


def test_timed_packet_program_is_complete_and_deterministic():
    data = workload()
    original = copy.deepcopy(data)
    text = packet_program(data)
    assert data == original and text == packet_program(data)
    assert len(text.splitlines()) == 64
    assert text.splitlines()[0] == "0 0 3 00000000"


def test_rejects_per_source_time_reversal_and_permanent_backpressure():
    data = workload()
    data["packets"][-1]["release_cycle"] = 0
    with pytest.raises(ValueError, match="nondecreasing"):
        packet_program(data)
    data = workload()
    data["sink_pause"] = data["sink_period"]
    with pytest.raises(ValueError, match="accept traffic"):
        packet_program(data)


@pytest.mark.parametrize("field,value", [("source", 4), ("payload", -1),
                                         ("release_cycle", 8192), ("source", True)])
def test_rejects_out_of_contract_packets(field, value):
    data = workload()
    data["packets"][0][field] = value
    with pytest.raises(jsonschema.ValidationError):
        packet_program(data)


def test_useful_work_floor_is_not_optional():
    data = workload()
    data["packets"].pop()
    with pytest.raises(jsonschema.ValidationError):
        packet_program(data)
