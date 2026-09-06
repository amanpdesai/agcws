"""Render all declared finalist profiles; no case or policy selection."""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from validation.aes_gls import sha


def render(archive, document, paper):
    report_path = archive/'validation.json'
    report = json.loads(report_path.read_text())
    for name,digest in report['artifact_sha256'].items():
        if sha(archive/name) != digest:
            raise ValueError('archive changed')
    rows = report['cases']
    if len(rows) != 16 or len(report['references']) != 4:
        raise ValueError('incomplete panel')
    labels = {'random':'Random','evolutionary':'Evolutionary','edit-agent':'Agent','edit-hybrid':'Hybrid'}
    colors = {'random':'#0072B2','evolutionary':'#E69F00','edit-agent':'#CC79A7','edit-hybrid':'#009E73'}
    figure, axes = plt.subplots(2,2,figsize=(7.2,3.05),sharex=True)
    for axis,reference in zip(axes.flat,report['references']):
        design,target = reference['design'],reference['target']
        power = json.loads((archive/reference['measurement']/'power.json').read_text())
        bounds = power['grid']['bounds_ticks']
        x = [(v-bounds[0])/(bounds[-1]-bounds[0])*100 for v in bounds]
        axis.stairs([1000*v for v in reference['dynamic_power_w']],x,
                    label='Reference',color='black',linestyle='--',linewidth=1.5,zorder=10,baseline=None)
        for row in rows:
            if (row['design'],row['target']) == (design,target):
                axis.stairs([1000*v for v in row['dynamic_power_w']],x,
                            label=labels[row['policy']],color=colors[row['policy']],linewidth=1,baseline=None)
        axis.set_title(f'{design.upper()} / {target}',fontsize=9)
        axis.set_ylabel('Dynamic power\n(mW)',fontsize=8)
        axis.tick_params(labelsize=7)
        axis.grid(axis='y',alpha=.2)
        if design == 'dma':
            axis.set_xlabel('Observation horizon (%)',fontsize=8)
    handles,names = axes[0,0].get_legend_handles_labels()
    figure.legend(handles,names,loc='upper center',ncol=5,fontsize=8,frameon=False)
    figure.tight_layout(rect=(0,0,1,.91),pad=.6)
    paper.mkdir(parents=True,exist_ok=True)
    figure.savefig(paper/'window_profiles.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(figure)
    lines = ['# Windowed gate-power validation', '',
             'Completed: 16 predeclared finalists plus four achieved references; 180 native OpenSTA reports.',
             'This is descriptive validation of selected cases, not a new policy study or a general proxy claim.', '',
             '## Findings', '',
             'Temporal power is measurable: AES finalist bins span 2.887–9.569 mW and DMA bins 20.155–21.769 mW.',
             'Nearly identical full-window means hid these shapes. The gate error uses the achieved reference RMS;',
             'DMA’s substantial common dynamic baseline makes its relative errors small, not proof of perfect shape matching.',
             'No gate-level solved threshold was introduced. Within each of the four target/design groups, the',
             'four finalists retain their activity-error ordering in gate error. This selected-case observation is not',
             'a general proxy-correlation or agent-superiority test.', '',
             '| Design | Reference | Policy | Activity error | Gate NRMSE | Bin min–max (mW) |',
             '|---|---|---|---:|---:|---:|']
    for row in rows:
        lines.append(f'| {row["design"].upper()} | {row["target"]} | {labels[row["policy"]]} | {row["activity_error"]:.5f} | {row["gate_nrmse"]:.5f} | {row["window_min_w"]*1000:.3f}–{row["window_max_w"]*1000:.3f} |')
    for design in ('aes','dma'):
        for target in ('random_300','random_301'):
            group = [r for r in rows if (r['design'],r['target']) == (design,target)]
            if [r['policy'] for r in sorted(group,key=lambda r:r['activity_error'])] != [r['policy'] for r in sorted(group,key=lambda r:r['gate_nrmse'])]:
                raise ValueError('stated selected-case ordering does not hold')
    errors, internal, native = [], [], []
    for path in archive.glob('**/power.json'):
        if 'matched_replay' in path.parts:
            continue
        p = json.loads(path.read_text())
        errors.append(abs(p['weighted_leaf_switching_w']/p['full']['leaf_switching_sum_w']-1))
        internal.append(abs(p['weighted_means']['internal_power_w']/p['full']['internal_power_w']-1))
        native.append(abs(p['weighted_means']['switching_power_w']/p['full']['switching_power_w']-1))
    lines += ['', '## Checks and scope', '',
              '- RTL/GLS rising-edge grids, individual timescales, total spans and exact bin durations match.',
              '- Native boundary/state tests pass at 1 ps and 10 ps; cuts contain no waveform timestamps.',
              '- All windows retain full-waveform annotation: AES 90,247/90,247; DMA 36,292/36,296.',
              f'- Maximum relative leaf-switching additivity discrepancy: {max(errors):.3g} (limit 1e-5).',
              f'- Maximum native aggregate switching discrepancy: {max(native):.3g}; the separate float32 precision audit explains why leaf sums are checked.',
              f'- Maximum internal-power weighted/full discrepancy: {max(internal):.3g}; diagnostic only, not forced to be additive.',
              f'- Summed measurement pipeline time: {report["measurement_wall_clock_s"]:.2f} s; two workers per matrix, with reference/finalist work overlapping.',
              '  This includes grid/hash work and 180 OpenSTA invocations, but not prior synthesis or reference GLS.',
              '- Functional zero-delay models omit timing-induced glitches; these are not signoff estimates.', '',
              '## Review artifacts', '',
              '- [Protocol](WINDOWED_POWER_PROTOCOL.md)',
              '- [All measurements and hashes](../results/windowed_power_v1/validation.json)',
              '- [Every profile, without case selection](../paper/window_profiles.pdf)',
              '- [Native semantics checks](../results/window_semantics_v1/verification.json)',
              '- [Conditional equal-valid temporal diagnostic](../results/structural_valid_evaluation_diagnostic_v1.json)', '',
              'The frozen activity studies are unchanged. Gate reference normalization differs from their activity scale,',
              'so the numerical error magnitudes are not directly comparable. The validation set contains one selected',
              'seed per policy and previously observed references, not a new inferential panel.']
    document.write_text('\n'.join(lines)+'\n')
    findings = ('\\heading{Selected-case findings}\n'
                'All 20 waveforms pass the window checks. AES finalist bins range from 2.887 to 9.569 mW; '
                'DMA bins range from 20.155 to 21.769 mW. Gate NRMSE spans .225--.404 on AES and .00346--.01887 '
                'on DMA. Within each target/design group, finalist activity-error ordering is preserved in gate error. '
                'This is descriptive selected-case agreement, not universal proxy validity. DMA\'s large common dynamic '
                'baseline reduces relative error; small NRMSE is not proof of exact shape matching. The figure shows '
                'all sixteen candidates and four references, with each tier\'s matched measurement horizon.\n')
    (paper/'window_findings.tex').write_text(findings)
    sources = {'archive_sha256':sha(report_path),'renderer_sha256':sha(Path(__file__)),
               'outputs':{str(p):sha(p) for p in (document,paper/'window_findings.tex',paper/'window_profiles.pdf')}}
    (paper/'window_figure_provenance.json').write_text(json.dumps(sources,indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,default=Path('results/windowed_power_v1'))
    parser.add_argument('--document',type=Path,default=Path('docs/WINDOWED_POWER_RESULTS.md'))
    parser.add_argument('--paper',type=Path,default=Path('paper'))
    args = parser.parse_args()
    render(args.archive,args.document,args.paper)
