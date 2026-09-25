import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('paper_overleaf', Path('paper/scripts/overleaf.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(tmp_path):
    (tmp_path / 'figures').mkdir()
    (tmp_path / 'evidence').mkdir()
    (tmp_path / 'report.tex').write_text(r'\documentclass[conference]{IEEEtran}\includegraphics{figures/a.pdf}')
    (tmp_path / 'figures/a.pdf').write_bytes(b'figure')
    files = module.dependencies(tmp_path)
    (tmp_path / 'evidence/build_provenance.json').write_text(json.dumps({
        'pages': 4, 'todo_count': 1,
        'inputs_and_outputs': {f'paper/{k}': module.digest(v) for k, v in files.items()}}))


def test_package_is_self_contained_and_deterministic(tmp_path):
    fixture(tmp_path)
    out = tmp_path / 'upload.zip'
    module.package(tmp_path, out)
    original = out.read_bytes()
    module.package(tmp_path, out)
    assert out.read_bytes() == original
    with zipfile.ZipFile(out) as archive:
        assert sorted(archive.namelist()) == ['README.md', 'SOURCE_MANIFEST.json', 'figures/a.pdf', 'main.tex']
        manifest = json.loads(archive.read('SOURCE_MANIFEST.json'))
        assert all(module.digest(archive.read(k)) == v for k, v in manifest['files'].items())


def test_changed_source_requires_rebuild(tmp_path):
    fixture(tmp_path)
    (tmp_path / 'report.tex').write_text('changed')
    with pytest.raises(ValueError, match='Rebuild'):
        module.package(tmp_path, tmp_path / 'upload.zip')


def test_package_includes_bibtex_and_checks_its_hash(tmp_path):
    fixture(tmp_path)
    with (tmp_path / 'report.tex').open('a') as source:
        source.write(r'\bibliographystyle{IEEEtran}\bibliography{references}')
    bibliography = tmp_path / 'references.bib'
    bibliography.write_text('@misc{example, title={Example}}')
    files = module.dependencies(tmp_path)
    (tmp_path / 'evidence/build_provenance.json').write_text(json.dumps({
        'pages': 4, 'todo_count': 1,
        'inputs_and_outputs': {f'paper/{k}': module.digest(v) for k, v in files.items()}}))
    output = tmp_path / 'upload.zip'
    module.package(tmp_path, output)
    with zipfile.ZipFile(output) as archive:
        assert archive.read('references.bib') == bibliography.read_bytes()
    bibliography.write_text('changed')
    with pytest.raises(ValueError, match='Rebuild'):
        module.package(tmp_path, output)


def test_dependencies_cannot_escape_paper_directory(tmp_path):
    paper = tmp_path / 'paper'
    paper.mkdir()
    (tmp_path / 'private.tex').write_text('private')
    (paper / 'report.tex').write_text(r'\input{../private.tex}')
    with pytest.raises(ValueError):
        module.dependencies(paper)


def test_overlength_bundle_warns_reader(tmp_path):
    fixture(tmp_path)
    receipt = tmp_path / 'evidence/build_provenance.json'
    build = json.loads(receipt.read_text())
    build['pages'] = 5
    receipt.write_text(json.dumps(build))
    output = tmp_path / 'upload.zip'
    module.package(tmp_path, output)
    with zipfile.ZipFile(output) as archive:
        assert b'WARNING: This working draft is 5 pages' in archive.read('README.md')
