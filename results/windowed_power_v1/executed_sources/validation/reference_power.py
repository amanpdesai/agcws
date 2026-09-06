"""Replay the four frozen achieved references, without generating new targets."""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.adapters.axi_dma.temporal import DmaTemporalAdapter
from agcws.workloads.schedule import ScheduleContract
from analysis.archive_matched_aes_gls import archive as archive_aes
from analysis.archive_matched_dma_gls import archive as archive_dma
from validation.aes_gls import sha


def reference(design, target, original, synthesis, out):
    frozen = json.loads(Path('results/structural_temporal_freeze_v1.json').read_text())
    entry = frozen['corpora'][design]
    corpus_path = Path(entry['path'])
    if sha(corpus_path) != entry['sha256']:
        raise ValueError('reference corpus changed')
    corpus = json.loads(corpus_path.read_text())
    case = next(c for c in corpus['cases'] if c['name'] == target)
    adapter = {'aes': AESTemporalAdapter, 'dma': DmaTemporalAdapter}[design](ScheduleContract(**corpus['contract']))
    lowered = adapter.elaborate(case['schedule'])
    if lowered != case['lowered_workload']:
        raise ValueError('reference lowering changed')
    activity = json.loads((original/'activity.json').read_text())
    n, samples = activity['clock_edges'], activity['per_cycle_toggles']
    rates = [sum(samples[i*n//8:(i+1)*n//8])/((i+1)*n//8-i*n//8) for i in range(8)]
    if n != case['clock_edges'] or rates != case['window_rates']:
        raise ValueError('raw RTL reference differs from recorded profile')
    if sha(original/'activity.vcd') != activity['waveform_sha256']:
        raise ValueError('raw reference waveform changed')
    out.mkdir(parents=True, exist_ok=False)
    rtl = original
    if design == 'dma':
        rtl = out/'rtl'
        (rtl/'sim_build').mkdir(parents=True)
        (rtl/'workload.json').write_text(json.dumps(lowered['workload'],sort_keys=True)+'\n')
        for name in ('activity.vcd','activity.json'):
            (rtl/name).symlink_to((original/name).resolve(strict=True))
        shutil.copy2(original/'sim_build/observed.json',rtl/'sim_build/observed.json')
        shutil.copy2(original.with_suffix('.log'),rtl/'driver.log')
        observed = json.loads((rtl/'sim_build/observed.json').read_text())
        if observed != case['observed'] or observed['trailing_idle_cycles'] != lowered['trailing_idle_cycles']:
            raise ValueError('DMA reference observations differ')
    elif json.loads((rtl/'workload.json').read_text()) != lowered:
        raise ValueError('AES reference workload differs')
    gls = out/'gls'
    command = [os.sys.executable,'-m',f'validation.{design}_gls']
    if design == 'aes':
        command += ['replay','--workload',str(rtl/'workload.json'),'--clock-edges',str(n)]
    else:
        command += ['--rtl',str(rtl)]
    command += ['--synthesis',str(synthesis),'--out',str(gls)]
    start = time.monotonic()
    with (out/'replay.log').open('w') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        script = 'scripts/run_opensta_aes.sh' if design == 'aes' else 'scripts/run_opensta_axi_dma.sh'
        subprocess.run(['bash',script,str(synthesis),str(gls/'activity.vcd'),str(gls/'power')],
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    (archive_aes if design=='aes' else archive_dma)(rtl,gls,synthesis,out/'archive')
    done = {'design':design,'target':target,'corpus_sha256':entry['sha256'],'schedule':case['schedule'],
            'rtl':str(rtl),'original_rtl':str(original),'clock_edges':n,
            'comparison_sha256':sha(out/'archive/comparison.json'),'wall_clock_s':time.monotonic()-start,
            'reference_driver_sha256':sha(Path(__file__))}
    (out/'completed.json').write_text(json.dumps(done,indent=2)+'\n')
    print('REFERENCE_GLS_VERIFIED',design,target,flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--design',choices=['aes','dma'],required=True)
    parser.add_argument('--target',choices=['random_300','random_301'],required=True)
    for name in ('original','synthesis','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    reference(args.design,args.target,args.original,args.synthesis,args.out)
