import json
from types import SimpleNamespace

import pytest

from validation.aes_gls import PARAMETERS, replay, sha


@pytest.mark.parametrize('change', ['parameters', 'netlist'])
def test_replay_rejects_stale_or_masked_netlist_before_simulation(tmp_path, change):
    synth = tmp_path / 'synth'
    synth.mkdir()
    netlist = synth / 'mapped.v'
    netlist.write_text('original netlist')
    manifest = {'parameters': dict(PARAMETERS), 'netlist_sha256': sha(netlist)}
    if change == 'parameters':
        manifest['parameters']['SecMasking'] = 1
    else:
        netlist.write_text('changed netlist')
    (synth / 'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='configuration or hash mismatch'):
        replay(SimpleNamespace(synthesis=synth), tmp_path)


def test_explicit_unmasked_lut_configuration():
    assert PARAMETERS == {'SecMasking': 0, 'SecSBoxImpl': 'aes_pkg::SBoxImplLut', 'EntropyWidth': 32}
