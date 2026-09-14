import runpy

from agcws.workloads.schedule import ScheduleContract, expand_schedule


def test_serial_proposals_preserve_work_and_idle_without_grouping():
    module = runpy.run_path("analysis/dma_serial_witnesses.py")
    requests = [{"id": str(i), "rates": [3, 5, 7, 9, 9, 7, 5, 3]} for i in range(9)]
    bank = {"calibration": {"domain": "dma-temporal", "low": 2},
            "splits": {name: {"requests": requests} for name in ("development", "confirmation")}}
    config = module["config"](bank)
    assert len(config["cases"]) == len({c["id"] for c in config["cases"]}) == 54
    for case in config["cases"]:
        sequence = expand_schedule(case["program"], ScheduleContract(64, 6000))
        work = [node for node in sequence if node["op"] == "work"]
        assert len(work) == 64 and all(node["units"] == 1 for node in work)
        assert len(sequence) <= 128
