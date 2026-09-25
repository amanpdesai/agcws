"""Strong-panel publication rejects mismatched tasks, trials and caches."""

import gzip
import importlib.util
import json
from pathlib import Path

import pytest

from agcws.reporting.metrics import error, key, max_bin_error, summarize

SPEC = importlib.util.spec_from_file_location('strong_paper', 'paper/scripts/extract_strong.py')
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def fixture(tmp_path, monkeypatch):
    arm = audit.ARM
    spec = dict(targets={'shape':[1.]*8,'flat_control':[1.]*8}, seeds=[1], policies=[arm],
                budget=128,batch_size=2,scale=1.,tolerance=.05,success_metric='max-bin')
    baseline = {'spec': {**spec, 'policies': list(audit.BASELINES)}}
    data = {'manifest.json':{'spec':spec,'measurement_fingerprint':{},'models':{}},
            'complete.json':{'cells':2},'continuation.json':{'manifest_sha256':'frozen'}}
    initial = {}
    for target in spec['targets']:
        program = {'target':target}
        rates = [1.02]*8
        cache = key({'program':program,'measurement':{}})
        trials = [dict(slot=n,valid=True,program=program,canonical_program=program,
                       rates=rates,cache_id=cache,loss=error(rates,[1.]*8,1.),
                       max_bin_error=max_bin_error(rates,[1.]*8,1.),residual=[.02]*8)
                  for n in (1,2)]
        for t in trials:
            t['residual'] = [r-1 for r in rates]
        prefix = f'panel/{target}/1/{arm}'
        identity = dict(target=target,seed=1,arm=arm,manifest_sha256='frozen')
        data[prefix+'/identity.json'] = identity
        data[prefix+'/batches/001/trials.json'] = trials
        data[prefix+'/batches/001/proposals.json'] = [dict(slot=n,program=program) for n in (1,2)]
        data[prefix+'/complete.json'] = {**summarize(trials,128,.05,stop_on_success=True,success_metric='max-bin'),'cell':identity}
        data[f'cache/{cache}/result.json'] = {'valid':True,'profile':{'window_rates':rates}}
        for other in audit.BASELINES:
            initial[f'panel/{target}/1/{other}/batches/001/trials.json'] = [dict(t) for t in trials]
    archive = tmp_path/'results/aes/strong-completed-v1'
    archive.mkdir(parents=True)
    (tmp_path / 'results/index.json').write_text(json.dumps({
        'version': 2, 'relocations': {}, 'designs': {'aes': {
            'gemini_3_8': 'results/aes/strong-completed-v1',
            'baselines': 'results/aes/baselines-model-v1'}}}))
    (archive/'retained-cache.json.gz').write_bytes(gzip.compress(b'{}'))
    (archive/audit.packs.PACK).write_bytes(b'fixture')
    monkeypatch.setattr(audit,'ROOT',tmp_path)
    monkeypatch.setattr(audit,'records',lambda p,pred: data if p.name=='strong-completed-v1' else initial)
    monkeypatch.setattr(audit.packs,'manifest',lambda p:{'run_manifest_sha256':'frozen'})
    return baseline,data,initial


def test_recompute_success_and_carry_forward(tmp_path, monkeypatch):
    baseline,_,_ = fixture(tmp_path,monkeypatch)
    result = audit.audit('aes',baseline)
    assert result['nonflat']['solved'] == result['control']['solved'] == 1
    assert result['nonflat']['charged_slots'] == 2
    assert result['nonflat']['mean_auc'] == pytest.approx(127*.02)


@pytest.mark.parametrize('corruption',['target','score','initial','completion','cache'])
def test_reject_corruption(tmp_path,monkeypatch,corruption):
    baseline,data,initial = fixture(tmp_path,monkeypatch)
    if corruption=='target':
        baseline['spec'] = {**baseline['spec'],'scale':2}
    elif corruption=='score':
        next(v for k,v in data.items() if k.endswith('/trials.json'))[0]['loss']=0.
    elif corruption=='initial':
        next(iter(initial.values()))[0]['program']={'different':True}
    elif corruption=='completion':
        next(v for k,v in data.items() if k.startswith('panel/') and k.endswith('/complete.json'))['auc']=0.
    else:
        next(v for k,v in data.items() if k.startswith('cache/'))['profile']['window_rates']=[0.]*8
    with pytest.raises(ValueError):
        audit.audit('aes',baseline)
