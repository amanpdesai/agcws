import runpy
from pathlib import Path

import pytest

validate_delivery = runpy.run_path("scripts/check_mesh_reference.py")["validate_delivery"]


@pytest.mark.parametrize("size", [2, 3])
def test_archived_mesh_delivery(size):
    log = Path(f"results/benchmark_readiness_v1/mesh{size}/run.log").read_text()
    result = validate_delivery(log, size)
    assert result["complete"] and result["delivered_packets"] == size ** 4


def test_success_marker_does_not_mask_missing_duplicate_or_wrong_packets():
    log = "[BSG_FINISH] test successful.\n(x,y)=(0,0) receiving id=0.\n"
    assert validate_delivery(log, 1)["complete"]
    for bad in (log.splitlines()[0], log + log.splitlines()[1], log.replace("id=0", "id=1"),
                log.replace("[BSG_FINISH] test successful.", "finished")):
        with pytest.raises(ValueError, match="every source"):
            validate_delivery(bad, 1)
