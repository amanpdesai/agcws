import runpy

from agcws.pipeline.ibex.program import allocation


def test_model_proposals_preserve_work_and_freeze_count():
    module = runpy.run_path("analysis/ibex_model_witnesses.py")
    probes = []
    for preset in range(3):
        for n in range(1, 9):
            probes.append({"id": f"preset-{preset}-divisions-{n}", "program": {
                "registers": [1]*8, "segments": [{"body": [{"op": "divu", "a": 0, "b": 1, "dst": 7}]*8}]},
                "measurement": {"valid": True, "profile": {"window_rates": [700]*8,
                "window_bit_transitions": [(700*200000-4096*(500+n*100))/8]*8},
                "execution": {"phases": {"segment_0_body": {"first_retired_cycle": 5, "last_retired_cycle": 4096*(10+n)+4}}}}})
    candidates = module["propose"]([400,400,600,600,400,400,600,600], probes)
    assert len(candidates) == len({c["variant"] for c in candidates}) == 12
    for c in candidates:
        assert sum(allocation(c["program"])) == 4096
        assert len(c["program"]["segments"]) == 8
