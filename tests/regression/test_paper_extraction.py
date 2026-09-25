"""Figure data are derived from immutable trials, never filled by hand."""

import gzip
import importlib.util
import io
import json
import tarfile
from pathlib import Path

import pytest

from agcws.evidence import packs

MODULE = Path(__file__).resolve().parents[2] / "paper/scripts/extract.py"
SPEC = importlib.util.spec_from_file_location("paper_extraction", MODULE)
figures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(figures)

checksum = figures.checksum


def snapshot(source, destination, recipe):
    """Build a small synthetic archive for extraction tests."""
    if destination.exists():
        raise FileExistsError(destination)
    paths = {source / "manifest.json"}
    arm = recipe["sources"]["Strong"]["arm"]
    for target in recipe["targets"]:
        cell = source / "panel" / target / str(recipe["seed"]) / arm
        paths.add(cell / "complete.json")
        paths.update(cell.glob("batches/*/trials.json"))
        paths.update(cell.glob("batches/*/response.json"))
    raw = {str(p.relative_to(source)): p.read_bytes() for p in sorted(paths)}
    raw["inventory.json"] = json.dumps({n: checksum(d) for n, d in raw.items()}, sort_keys=True).encode()
    destination.mkdir(parents=True)
    metadata = {"version": 1, "kind": "selected-completed-cells-not-full-study", "files": {}, "shards": {}}
    shard = destination / "evidence-000.tar.gz"
    with shard.open("xb") as stream:
        with gzip.GzipFile(fileobj=stream, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT) as archive:
                for name, data in sorted(raw.items()):
                    data = gzip.compress(data, mtime=0)
                    item = tarfile.TarInfo(name + ".gz")
                    item.size, item.mode, item.mtime = len(data), 0o644, 0
                    archive.addfile(item, io.BytesIO(data))
                    metadata["files"][item.name] = {"size": len(data), "mode": item.mode, "sha256": checksum(data)}
    metadata["shards"][shard.name] = packs.sha(shard)
    (destination / packs.PACK).write_bytes(gzip.compress(json.dumps(metadata, sort_keys=True).encode(), mtime=0))
    packs.verify(destination)


def fixture(tmp_path, monkeypatch, reported_error=.02):
    recipe = {"design": "mesh", "seed": 9100, "targets": ["burst"],
              "scope": "test", "selection": "minimum max-bin then earliest slot",
              "sources": {"Strong": {"archive": "paper/evidence/snapshot", "arm": "strong"}}}
    (tmp_path / "paper/evidence").mkdir(parents=True)
    (tmp_path / 'results').mkdir()
    (tmp_path / 'results/index.json').write_text(json.dumps({'version': 2, 'relocations': {}}))
    (tmp_path / "paper/evidence/figure_recipe.json").write_text(json.dumps(recipe))
    source = tmp_path / "live"
    cell = source / "panel/burst/9100/strong"
    batch = cell / "batches/001"
    batch.mkdir(parents=True)
    (source / "manifest.json").write_text(json.dumps({
        "spec": {"scale": 10, "tolerance": .05, "budget": 128, "success_metric": "max-bin",
                 "targets": {"burst": [1] * 8}}, "runtime": {"image_id": "frozen"}, "schema": {}}))
    (batch / "trials.json").write_text(json.dumps([
        {"valid": True, "rates": [1.2] * 8, "profile": {}, "canonical_program": {"op": "first"}},
        {"valid": True, "rates": [1.2] * 8, "profile": {}, "canonical_program": {"op": "second"}},
    ]))
    (cell / "complete.json").write_text(json.dumps({
        "charged_slots": 2, "best_max_bin_error": reported_error,
        "cell": {"target": "burst", "seed": 9100, "arm": "strong"}}))
    destination = tmp_path / "paper/evidence/snapshot"
    snapshot(source, destination, recipe)
    monkeypatch.setattr(figures, "ROOT", tmp_path)
    return recipe, source, destination


def test_extraction_uses_archive_and_earliest_tie(tmp_path, monkeypatch):
    recipe, source, destination = fixture(tmp_path, monkeypatch)
    (source / "manifest.json").write_text("not used after capture")
    result = figures.extract(recipe)["cases"][0]["arms"]["Strong"]
    assert result["max_bin_error"] == pytest.approx(.02)
    assert result["selected_slot"] == 1
    assert result["program"] == {"op": "first"}
    assert len(result["source_sha256"]) == 64
    with pytest.raises(FileExistsError):
        snapshot(source, destination, recipe)


def test_extraction_rejects_completion_disagreement(tmp_path, monkeypatch):
    recipe, _, _ = fixture(tmp_path, monkeypatch, reported_error=.001)
    with pytest.raises(ValueError, match="discrepancy"):
        figures.extract(recipe)


def test_extraction_does_not_require_strong_arm(tmp_path, monkeypatch):
    recipe, _, _ = fixture(tmp_path, monkeypatch)
    recipe['sources']['Flash-Lite'] = recipe['sources'].pop('Strong')
    result = figures.extract(recipe)
    assert set(result['cases'][0]['arms']) == {'Flash-Lite'}


def test_task_vectors_match_frozen_banks():
    tasks = figures.extract_tasks()
    assert len(tasks) == 5
    assert sum(len(t['targets']) for t in tasks.values()) == 45
    assert tasks['redmule']['domain'] == 'redmule-temporal-long'
    assert tasks['mesh']['sources']['bank']['path'] == 'results/mesh/tasks/bank.json'
    aes = tasks['aes']['targets']
    assert sum(aes['confirmation-burst']) == pytest.approx(sum(aes['confirmation-alternating']))


@pytest.mark.parametrize('changed', ['bank', 'config'])
def test_task_extraction_rejects_modified_sources(tmp_path, monkeypatch, changed):
    tasks = figures.extract_tasks()
    (tmp_path / 'results').mkdir()
    (tmp_path / 'results/index.json').write_bytes((figures.ROOT / 'results/index.json').read_bytes())
    for task in tasks.values():
        for source in task['sources'].values():
            relative = source['path']
            destination = tmp_path / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((figures.ROOT / relative).read_bytes())
    path = tmp_path / tasks['aes']['sources'][changed]['path']
    data = json.loads(path.read_text())
    if changed == 'bank':
        data['calibration']['scale'] += 1
    else:
        data['targets']['confirmation-burst'][0] += 1
    path.write_text(json.dumps(data))
    monkeypatch.setattr(figures, 'ROOT', tmp_path)
    with pytest.raises(ValueError, match='mismatch'):
        figures.extract_tasks()
