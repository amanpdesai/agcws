import runpy

import pytest

from agcws.pipeline.storage import write


def test_bin_constructor_preserves_requests_and_emits_all_roundings(tmp_path):
    rows = []
    for size in (4, 8, 16):
        for pattern in ("zeros", "alternating", "random"):
            for mult in (1, 2):
                rows.append({"id": f"size{size}-{pattern}-x{mult}",
                             "measurement": {"valid": True, "rates": [2+mult]*8},
                             "program": {"phases": [{"jobs": mult}]}})
    write(tmp_path / "complete.json", {"results": rows})
    write(tmp_path / "manifest.json", {"measurement": {"measurement_fingerprint": "same"}})
    bank = {"calibration": {"measurement_fingerprint": "same"}, "splits": {
        split: {"requests": [{"id": str(i), "rates": [14]*8} for i in range(9)]}
        for split in ("development", "confirmation")}}
    make = runpy.run_path("analysis/redmule_bin_witness.py")["make_config"]
    config = make(tmp_path, bank)
    assert len(config["cases"]) == len({c["id"] for c in config["cases"]}) == 486
    assert [p["jobs"] for p in config["cases"][0]["program"]["phases"]] == [1]*8
    assert [p["jobs"] for p in config["cases"][1]["program"]["phases"]] == [2]*8
    assert bank["splits"]["development"]["requests"][0]["rates"] == [14]*8
    bank["calibration"]["measurement_fingerprint"] = "different"
    with pytest.raises(ValueError, match="fingerprints differ"):
        make(tmp_path, bank)
