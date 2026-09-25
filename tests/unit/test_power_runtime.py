import hashlib
import json

import pytest

from agcws.evidence import power_runtime


def test_exact_sources_restored_without_copying_secrets_or_mutating_template(tmp_path, monkeypatch):
    template, out = tmp_path / 'template', tmp_path / 'restored'
    template.mkdir()
    (template / 'module.py').write_text('new')
    (template / '.env').write_text('private')
    expected = hashlib.sha256(b'old').hexdigest()
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'sources': {'module.py': expected}}))
    monkeypatch.setattr(power_runtime, 'recover_blob', lambda *args: (b'old', 'frozen-commit'))
    receipt = power_runtime.prepare([manifest], template, out, tmp_path)
    assert (out / 'module.py').read_text() == 'old'
    assert (template / 'module.py').read_text() == 'new'
    assert not (out / '.env').exists()
    assert receipt['sources_verified']
    with pytest.raises(ValueError, match='must be new'):
        power_runtime.prepare([manifest], template, out, tmp_path)


def test_conflicting_manifests_fail_before_creating_runtime(tmp_path):
    paths = []
    for name, digest in [('a', 'first'), ('b', 'second')]:
        path = tmp_path / f'{name}.json'
        path.write_text(json.dumps({'sources': {'module.py': digest}}))
        paths.append(path)
    with pytest.raises(ValueError, match='different source versions'):
        power_runtime.prepare(paths, tmp_path, tmp_path / 'out', tmp_path)
    assert not (tmp_path / 'out').exists()
