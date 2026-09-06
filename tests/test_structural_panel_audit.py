import json
import shutil
from pathlib import Path

import pytest

from analysis.audit_structural_panel import audit_cell

SOURCE = Path('results/structural_temporal_dma_four_arm_v2/random_300/edit-agent')


def test_known_cell_recomputes():
    row, _, _ = audit_cell(SOURCE, 'dma', 'random_300', 310, 'edit-agent', 16)
    assert row['valid_trials'] == 14


@pytest.mark.parametrize('field,value', [('auc_best_so_far', 0), ('right_censored', True),
                                        ('valid_trials', 16), ('tokens_in', 0)])
def test_corrupted_summary_rejected(tmp_path, field, value):
    cell = tmp_path / 'cell'
    shutil.copytree(SOURCE, cell)
    path = cell / 'summary.json'
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        audit_cell(cell, 'dma', 'random_300', 310, 'edit-agent', 16)
