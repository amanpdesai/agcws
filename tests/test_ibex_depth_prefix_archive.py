import pytest

from analysis.ibex_depth_v1 import completed_prefixes
from experiments.ibex_depth_v1.storage import write


def test_only_complete_ordered_panels_can_be_archived(tmp_path):
    manifest = {"prefixes": [16, 64, 128], "cells": [1, 2]}
    with pytest.raises(ValueError, match="no complete"):
        completed_prefixes(tmp_path, manifest)
    write(tmp_path / "prefix-16-complete.json", {"cells": 2, "slots": 32})
    assert completed_prefixes(tmp_path, manifest) == [16]
    write(tmp_path / "prefix-128-complete.json", {"cells": 2, "slots": 256})
    with pytest.raises(ValueError, match="ordered"):
        completed_prefixes(tmp_path, manifest)
    write(tmp_path / "prefix-64-complete.json", {"cells": 2, "slots": 128})
    assert completed_prefixes(tmp_path, manifest) == [16, 64, 128]
