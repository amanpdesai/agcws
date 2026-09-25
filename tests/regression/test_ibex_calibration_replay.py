from agcws.evidence.replay import comparable_ibex as compare


def test_only_extraction_wall_time_is_excluded_from_profile_comparison():
    r = {"valid": True, "stage": None, "profile": {"window_rates": [1]*8, "waveform_sha256": "x", "extraction_s": 1}}
    assert compare(r) == compare({**r, "profile": {**r["profile"], "extraction_s": 100}})
    assert compare(r) != compare({**r, "profile": {**r["profile"], "waveform_sha256": "y"}})
