import json
from pathlib import Path

import pytest

from agcws.designs.dma import gls


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rtl, synthesis = tmp_path / 'rtl', tmp_path / 'synthesis'
    rtl.mkdir()
    synthesis.mkdir()
    sources = {}
    for name in ('axi_dma.v', 'axi_dma_rd.v', 'axi_dma_wr.v'):
        path = Path('benchmarks/verilog-axi/rtl') / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
        sources[str(path)] = gls.sha(path)
    liberty = tmp_path / 'cells.lib'
    liberty.write_text('library')
    monkeypatch.setattr(gls.config, 'LIBERTY', liberty)
    (synthesis / 'mapped.v').write_text('netlist')
    mapped = dict(top='axi_dma', sources=sources,
                  netlist_sha256=gls.sha(synthesis / 'mapped.v'),
                  liberty_sha256=gls.sha(liberty))
    (synthesis / 'manifest.json').write_text(json.dumps(mapped))
    manifest = {'backend': 'axi_dma_pipelined_tb'}
    for name, field in [('workload.json', 'workload_sha256'),
                        ('activity.json', 'activity_sha256'),
                        ('activity.vcd', 'waveform_sha256')]:
        (rtl / name).write_text(name)
        manifest[field] = gls.sha(rtl / name)
    (rtl / 'manifest.json').write_text(json.dumps(manifest))
    return rtl, synthesis, mapped


def test_validated_inputs(inputs):
    rtl, synthesis, mapped = inputs
    assert gls.validate_inputs(rtl, synthesis) == mapped


@pytest.mark.parametrize('field,value,message', [
    ('sources', {}, 'complete RTL source inventory'),
    ('netlist_sha256', 'bad', 'checksum/top'),
    ('liberty_sha256', 'bad', 'Liberty'),
    ('memory_manifest', 'macro.json', 'macro-mapped'),
])
def test_reject_unverifiable_synthesis(inputs, field, value, message):
    rtl, synthesis, mapped = inputs
    mapped[field] = value
    (synthesis / 'manifest.json').write_text(json.dumps(mapped))
    with pytest.raises(ValueError, match=message):
        gls.validate_inputs(rtl, synthesis)


@pytest.mark.parametrize('name', ['workload.json', 'activity.json', 'activity.vcd'])
def test_reject_changed_replay(inputs, name):
    rtl, synthesis, _ = inputs
    (rtl / name).write_text('changed')
    with pytest.raises(ValueError, match='RTL replay input differs'):
        gls.validate_inputs(rtl, synthesis)


def test_reject_changed_rtl(inputs):
    rtl, synthesis, mapped = inputs
    Path(next(iter(mapped['sources']))).write_text('changed')
    with pytest.raises(ValueError, match='sources differ'):
        gls.validate_inputs(rtl, synthesis)
