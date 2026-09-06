"""Power-valued normalization is reference-based and duration-weighted."""
import json
import math
import shutil
from pathlib import Path

import pytest

from analysis.audit_windowed_archive import audit
from analysis.windowed_finalists import nrmse


def test_reference_normalization():
    reference = [2.0]*8
    durations = [1.0]*8
    assert nrmse(reference,reference,durations) == 0
    assert nrmse([4.0]*8,reference,durations) == 1
    assert nrmse([0.0]*8,reference,durations) == 1
    assert nrmse([3.0]*8,reference,durations) == 0.5


def test_duration_weighting():
    assert nrmse([2.0]+[1.0]*7,[1.0]*8,[9.0]+[1.0]*7) == 0.75
    assert math.isclose(nrmse([2.0]+[1.0]*7,[1.0]*8,[1.0]*8),math.sqrt(1/8))


@pytest.mark.parametrize('candidate,reference,durations', [
    ([1.0]*7,[1.0]*8,[1.0]*8),
    ([1.0]*8,[0.0]*8,[1.0]*8),
    ([float('nan')]*8,[1.0]*8,[1.0]*8),
    ([1.0]*8,[1.0]*8,[0.0]*8),
])
def test_invalid_measurements(candidate,reference,durations):
    with pytest.raises(ValueError):
        nrmse(candidate,reference,durations)


def test_complete_compact_archive():
    result = audit(Path('results/windowed_power_v1'))
    assert result['verified_reports'] == 180
    assert result['verified_finalists'] == 16


def test_tampered_gate_error_rejected(tmp_path):
    root = tmp_path/'archive'
    shutil.copytree('results/windowed_power_v1',root)
    path = root/'validation.json'
    data = json.loads(path.read_text())
    data['cases'][0]['gate_nrmse'] += .1
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='error changed'):
        audit(root)


def test_tampered_raw_report_rejected(tmp_path):
    root = tmp_path/'archive'
    shutil.copytree('results/windowed_power_v1',root)
    path = next(root.glob('finalists/*/bin-0.rpt'))
    path.write_text(path.read_text()+'tampered\n')
    with pytest.raises(ValueError,match='changed artifact'):
        audit(root)
