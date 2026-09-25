import json
from pathlib import Path

import pytest

from agcws.evidence import catalog


def test_final_paths_and_recorded_identities():
    root = Path.cwd()
    for design in ('aes', 'dma', 'ibex', 'mesh', 'redmule'):
        archive = catalog.design(root, design, 'gemini_3_8')
        assert archive.is_dir()
        old = f'results/{design}/strong-completed-v1'
        assert catalog.resolve(root, old) == archive
        assert catalog.recorded(root, archive) == old
    assert catalog.summary(root, 'baselines').is_file()


@pytest.mark.parametrize('name', ['/tmp/private', '../private', 'results/../../private'])
def test_catalog_rejects_unsafe_paths(name):
    with pytest.raises(ValueError, match='unsafe'):
        catalog.resolve(Path.cwd(), name)


def test_relocations_cannot_escape_checkout(tmp_path):
    (tmp_path / 'results').mkdir()
    (tmp_path / 'results/index.json').write_text(json.dumps({
        'version': 2, 'relocations': {'old': '../outside'}}))
    with pytest.raises(ValueError, match='unsafe'):
        catalog.resolve(tmp_path, 'old')
