"""Render the current archived comparison and compile the working paper."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

from agcws.evidence import catalog

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
INPUTS = [str(catalog.summary(ROOT, name).relative_to(ROOT)) for name in
          ('flash_lite', 'baselines', 'flash_secondary', 'gemini_3_8', 'power')]
DESIGNS = {"aes": "AES", "dma": "DMA", "ibex": "Ibex", "mesh": "Mesh", "redmule": "RedMulE"}
ARMS = {
    "flash-lite-medium": "Flash-Lite",
    "phase-random": "Phase-random",
    "phase-ga": "Phase-GA",
    "phase-model": "Phase-model",
    "strong-medium-64k": "Gemini 3.8",
}
POLICY_STYLES = {
    "phase-random": dict(color="#9c6c22", marker="^", linestyle=":"),
    "phase-ga": dict(color="#d45b35", marker="s", linestyle="--"),
    "phase-model": dict(color="#64788b", marker="D", linestyle="-."),
    "flash-lite-medium": dict(color="#7855a2", marker="o", linestyle="-"),
    "strong-medium-64k": dict(color="#007c83", marker="P", linestyle="-"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pending_table_cells(figures):
    return sum(p.read_text().count(r"\pending") for p in figures.glob("*.tex"))


def render_system(figures):
    """Execution order and the activity-only selection boundary."""
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.set(xlim=(0, 10), ylim=(0, 5.2))
    ax.axis("off")

    def box(x, y, w, h, text, color="#eef1f4"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.025",
                                   facecolor=color, edgecolor="#42566b", linewidth=0.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def arrow(*points):
        if len(points) > 2:
            ax.plot(*zip(*points[:-1]), color="#42566b", lw=.9)
        ax.annotate("", points[-1], points[-2],
                    arrowprops={"arrowstyle": "->", "lw": .9, "color": "#42566b"})

    ax.text(.1, 5.0, "ACTIVITY-GUIDED SEARCH", fontsize=8, weight="bold")
    box(.1, 4.35, 9.8, .43, "Shared task specification: target, scale, horizon, work and tolerance")
    arrow((1, 4.35), (1, 3.72))
    arrow((6.2, 4.35), (6.2, 4.02))
    box(.1, 2.9, 1.85, .8, "Proposal policy\nLLM / classical", "#e1eef6")
    ax.add_patch(FancyBboxPatch((3.15, 2.74), 6.72, 1.25,
        boxstyle="round,pad=0.025", facecolor="none", edgecolor="#8b98a5", lw=.8))
    ax.text(3.3, 3.81, "Shared evaluator", fontsize=8)
    box(3.3, 2.92, 1.75, .68, "Check and translate\nworkload")
    box(5.42, 2.92, 1.42, .68, "RTL\nSimulation")
    box(7.22, 2.92, 2.5, .68, "Functional / work / deadline\nchecks + activity")
    arrow((1.98, 3.3), (3.27, 3.3))
    ax.text(2.62, 3.44, "candidate", ha="center", fontsize=8)
    arrow((5.08, 3.3), (5.39, 3.3))
    arrow((6.87, 3.3), (7.19, 3.3))
    box(4.7, 1.93, 3.4, .51, "Recorded workload and outcome", "#e4f0e9")
    arrow((4.15, 2.9), (4.15, 2.18), (4.68, 2.18))
    ax.text(4.02, 2.52, "reject", ha="right", fontsize=8)
    arrow((8.45, 2.9), (8.45, 2.18), (8.13, 2.18))
    arrow((4.67, 2.08), (1, 2.08), (1, 2.87))
    ax.text(2.65, 2.17, "evaluation feedback", ha="center", fontsize=8)
    ax.text(.1, 1.47, "POST-SEARCH MAPPED-POWER ASSESSMENT", fontsize=8, weight="bold")
    box(.1, .52, 2.55, .68, "Cached mapped design\nNetlist + Liberty + clock")
    box(3.05, .65, 2.15, .55, "Reference workload")
    box(5.65, 1.04, 1.65, .53, "Select and freeze\nworkload", "#e1eef6")
    arrow((6.48, 1.92), (6.48, 1.6))
    ax.text(6.62, 1.73, "valid candidates", fontsize=8, va="center")
    box(5.55, .08, 1.85, .62, "Matched\ngate replay", "#f7eddb")
    box(7.88, .08, 2.02, .62, "Estimated dynamic\npower (OpenSTA)", "#f7eddb")
    arrow((6.48, 1.01), (6.48, .73))
    arrow((5.22, .91), (5.38, .91), (5.38, .5), (5.52, .5))
    arrow((2.68, .85), (2.8, .85), (2.8, .25), (5.52, .25))
    arrow((7.43, .39), (7.85, .39))
    fig.subplots_adjust(left=.01, right=.99, bottom=.02, top=.99)
    fig.savefig(figures / "architecture.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def render_waveforms(figures):
    evidence = json.loads((PAPER / "evidence/mesh_examples.json").read_text())
    recipe = json.loads((PAPER / "evidence/figure_recipe.json").read_text())
    order = recipe["display_order"]
    emphasis = recipe["annotation_policies"]
    columns = recipe["legend_columns"]
    if columns < 1 or len(set(order)) != len(order):
        raise ValueError("Invalid waveform presentation settings")
    labels = set(evidence["cases"][0]["arms"])
    if (not labels.issubset(order) or not emphasis
            or len(set(emphasis)) != len(emphasis)
            or not set(emphasis).issubset(labels)):
        raise ValueError("Waveform policies missing from presentation settings")
    legend_rows = int(np.ceil((1 + len(labels)) / columns))
    height = 2.45 + .22 * (legend_rows - 1)
    fig, axes = plt.subplots(1, 2, figsize=(7, height), sharey=True)
    for panel, (ax, case) in enumerate(zip(axes, evidence["cases"], strict=True)):
        target = np.asarray(case["target_rates"]) / evidence["scale"]
        x = np.arange(9)
        ax.fill_between(x, np.r_[target - .05, target[-1] - .05],
                        np.r_[target + .05, target[-1] + .05], step="post", color="#d5dadd", alpha=.65)
        ax.stairs(target, x, baseline=None, color="black", linewidth=1.0, label="Target", zorder=2)
        if set(case["arms"]) != labels:
            raise ValueError("Waveform panels must show the same policies")
        for label in order:
            if label not in labels:
                continue
            row = case["arms"][label]
            rates = np.asarray(row["rates"]) / evidence["scale"]
            error = float(np.max(np.abs(rates - target)))
            if not np.isclose(error, row["max_bin_error"]):
                raise ValueError("Waveform evidence/error disagreement")
            if recipe['sources'][label]['arm'] == 'strong-medium-64k' and row["model"] != "gemini-3.8-flash":
                raise ValueError("Strong-model label does not match response metadata")
            display = "Gemini 3.8 Flash" if label == "Strong" else label
            style = POLICY_STYLES[recipe["sources"][label]["arm"]]
            ax.stairs(rates, x, baseline=None, color=style["color"],
                      linestyle=style["linestyle"], linewidth=1.05, zorder=3)
            ax.plot(np.arange(8) + .5, rates, linestyle="none", marker=style["marker"],
                    color=style["color"], markersize=3.3, zorder=4)
            # Separate legend handles retain the line style without interpolating bin means.
            ax.plot([], [], **style, linewidth=1.05, markersize=3.3, label=display)
        ax.set_title(f"({chr(97 + panel)}) " + case["target"].removeprefix("confirmation-").capitalize(), fontsize=9)
        ax.set(xlim=(0, 8), xticks=np.arange(8) + .5, xticklabels=np.arange(1, 9), xlabel="Observation bin")
        ax.grid(axis="y", alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
        fig.text(.32 if panel == 0 else .79, (.22 * legend_rows + .10) / height,
                 "\n".join(f"{label}: {case['arms'][label]['charged_slots']} charged proposals"
                           for label in emphasis), ha="center", fontsize=8)
    axes[0].set_ylabel(r"Normalized RTL activity, $a_k/s_d$", fontsize=8)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    # Matplotlib fills legend columns first; reorder handles for row-major display.
    indices = [i for col in range(columns) for i in range(col, len(handles), columns)]
    fig.legend([handles[i] for i in indices], [legend_labels[i] for i in indices],
               loc="lower center", ncol=columns,
               fontsize=8, frameon=False, columnspacing=1.1, handlelength=2)
    fig.subplots_adjust(left=.095, right=.99, top=.89,
                        bottom=(1.02 + .22 * (legend_rows - 1)) / height, wspace=.1)
    fig.savefig(figures / "mesh_waveforms.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def render():
    flash, baseline = [json.loads((ROOT / p).read_text()) for p in INPUTS[:2]]
    strong = json.loads((ROOT / INPUTS[3]).read_text())
    if strong['baseline_summary_sha256'] != digest(ROOT / INPUTS[1]):
        raise ValueError('Strong summary is not paired with this baseline archive')
    if strong['extractor_sha256'] != digest(PAPER / 'scripts/extract_strong.py'):
        raise ValueError('Regenerate the strong summary with the current extractor')
    from agcws.evidence import packs
    for result in strong['designs'].values():
        archive = catalog.resolve(ROOT, result['archive'])
        if (digest(archive / packs.PACK) != result['archive_manifest_sha256'] or
                digest(archive / 'retained-cache.json.gz') != result['retained_cache_sha256']):
            raise ValueError('Strong evidence changed after audit')
        for shard, expected in packs.manifest(archive)['shards'].items():
            if digest(archive / shard) != expected:
                raise ValueError('Strong evidence shard changed after audit')
    if flash["baseline_summary_sha256"] != digest(ROOT / INPUTS[1]):
        raise ValueError("Flash summary is not paired with this baseline archive")
    plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 5, figsize=(7, 2.15), sharex=True, sharey=True)
    largest_mean = 0.0
    table = [r"\begin{tabular}{lrrrrr}", r"\toprule",
             r"Design & Flash-Lite & Phase-random & Phase-GA & Phase-model & Gemini 3.8 \\", r"\midrule"]
    for ax, (name, label) in zip(axes, DESIGNS.items(), strict=True):
        data = flash["designs"][name]
        cells = data["cells"] + baseline["designs"][name]["cells"] + strong['designs'][name]['cells']
        values = {**data["nonflat_by_arm"], 'strong-medium-64k': strong['designs'][name]['nonflat']}
        best = min(v["mean_auc"] for v in values.values())
        row = [label]
        for arm, legend in ARMS.items():
            subset = [c for c in cells if c["arm"] == arm and not c["target"].endswith("flat_control")]
            identities = {(c["target"], c["seed"]) for c in subset}
            if len(subset) != 80 or len(identities) != 80 or any(c["budget"] != 128 for c in subset):
                raise ValueError(f"Incomplete or duplicate nonflat panel: {name}/{arm}")
            curves = np.asarray([c["curve"] for c in subset])
            if curves.shape != (80, 128) or not np.isfinite(curves).all():
                raise ValueError(f"Invalid archived curves: {name}/{arm}")
            auc = float(np.mean([c["auc"] for c in subset]))
            solved = sum(c["solved"] for c in subset)
            if not np.isclose(auc, values[arm]["mean_auc"]) or solved != values[arm]["solved"]:
                raise ValueError(f"Summary/curve panel disagreement: {name}/{arm}")
            mean = curves.mean(axis=0)
            largest_mean = max(largest_mean, float(mean.max()))
            ax.plot(np.arange(1, 129), mean, label=legend, linewidth=1.15,
                    **POLICY_STYLES[arm], markevery=32, markersize=2.5)
            number = f"{auc:.2f}"
            if values[arm]["mean_auc"] == best:
                number = r"\textbf{" + number + "}"
            row.append(f"{number} / {solved}")
        table.append(" & ".join(row) + r" \\")
        ax.set_title(label)
        ax.set_xlim(1, 128)
        ax.set_xticks([1, 64, 128])
        ax.grid(alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Mean incumbent\nnormalized RMS error")
    axes[0].set_ylim(0, largest_mean * 1.05)
    fig.supxlabel("Charged proposal slots", y=0.17, fontsize=8)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=5, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.22, 1, 1), pad=0.4, w_pad=0.5)
    figures = PAPER / "figures"
    figures.mkdir(exist_ok=True)
    supplementary = figures / "supplementary"
    supplementary.mkdir(exist_ok=True)
    fig.savefig(supplementary / "matched_curves.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    table.extend([r"\bottomrule", r"\end{tabular}"])
    (supplementary / "matched_table.tex").write_text("\n".join(table) + "\n")
    final = [r"\begin{tabular}{l*{5}{rr}}", r"\toprule",
             r"Design & \multicolumn{2}{c}{Phase-random} & \multicolumn{2}{c}{Phase-GA} & \multicolumn{2}{c}{Phase-model} & \multicolumn{2}{c}{Flash-Lite} & \multicolumn{2}{c}{Gemini 3.8} \\",
             r" & AUC $\downarrow$ & Solves & AUC $\downarrow$ & Solves & AUC $\downarrow$ & Solves & AUC $\downarrow$ & Solves & AUC $\downarrow$ & Solves \\",
             r"\midrule"]
    efficiency = [r"\begin{tabular}{lrrrr}", r"\toprule",
                  r"Design & \shortstack{Capped\\first-hit slot} & \shortstack{Valid\\slots (\%)} & \shortstack{Known\\usage (\$)} & \shortstack{Total incl.\\reserves (\$)} \\",
                  r"\midrule"]
    secondary = json.loads((ROOT / INPUTS[2]).read_text())
    for name, label in DESIGNS.items():
        values = {**flash['designs'][name]['nonflat_by_arm'], 'strong-medium-64k': strong['designs'][name]['nonflat']}
        best = min(v['mean_auc'] for v in values.values())
        row = [label]
        for arm in ('phase-random', 'phase-ga', 'phase-model', 'flash-lite-medium', 'strong-medium-64k'):
            auc = f"{values[arm]['mean_auc']:.2f}"
            row.extend([r'\textbf{' + auc + '}' if values[arm]['mean_auc'] == best else auc,
                        str(values[arm]['solved'])])
        final.append(' & '.join(row) + r' \\')
        arm = values['flash-lite-medium']
        cost = secondary[name]['cost_per_solve']['nonflat']
        efficiency.append(' & '.join([label,
            f"{arm['mean_evaluations_to_target_censored']:.1f}",
            f"{100 * arm['valid_slots'] / arm['charged_slots']:.1f}",
            f"{cost['known_usage_subtotal_usd']:.2f}",
            f"{cost['conservative_liability_usd']:.2f}"]) + r' \\')
    for filename, rows in [('final_table.tex', final), ('supplementary/flash_efficiency.tex', efficiency)]:
        (figures / filename).write_text('\n'.join([*rows, r'\bottomrule', r'\end{tabular}']) + '\n')
    render_system(figures)
    render_waveforms(figures)
    render_power(figures)


def render_power(figures):
    power = json.loads((ROOT / INPUTS[4]).read_text())
    if power['extractor_sha256'] != digest(PAPER / 'scripts/extract_power.py'):
        raise ValueError('Regenerate power analysis with the current extractor')
    for path, expected in power['inputs'].items():
        if digest(catalog.resolve(ROOT, path)) != expected:
            raise ValueError('Power evidence changed after analysis')
    rows = [r'\begin{tabular}{lrrr}', r'\toprule',
            r'Design & Gemini 3.8 & Classical & $n$ \\', r'\midrule']
    for name,label in DESIGNS.items():
        matched = power['designs'][name]['matched_strong']
        selected = min(('phase-random','phase-ga','phase-model'),
                       key=lambda a:matched[a]['comparator']['mean_nrmse'])
        pair = matched[selected]
        rows.append(f"{label} & {100*pair['strong']['mean_nrmse']:.3f} & "
                    f"{100*pair['comparator']['mean_nrmse']:.3f} & {pair['strong']['n']}" + r' \\')
    (figures/'power_table.tex').write_text('\n'.join([*rows,r'\bottomrule',r'\end{tabular}'])+'\n')
    fig, axes = plt.subplots(2, 2, figsize=(7, 4.5), sharex=True)
    for col, case in enumerate(power['illustrations']):
        reference=np.asarray(case['reference']['gate_dynamic_power_w'])
        duration=np.asarray(case['reference']['power']['grid']['durations_s'])
        scale=float(np.dot(reference,duration)/duration.sum())
        axes[0,col].stairs(reference*1000,np.arange(9),baseline=None,color='black',label='Reference workload')
        for arm in ('phase-random','phase-ga','phase-model','flash-lite-medium','strong-medium-64k'):
            values=np.asarray(case['candidates'][arm]['gate_dynamic_power_w'])
            style=POLICY_STYLES[arm]
            for row,y in ((0,values*1000),(1,(values-reference)/scale)):
                axes[row,col].stairs(y,np.arange(9),baseline=None,color=style['color'],linestyle=style['linestyle'])
                axes[row,col].plot(np.arange(8)+.5,y,linestyle='none',marker=style['marker'],markersize=3,color=style['color'])
            axes[0,col].plot([],[],**style,label=ARMS[arm])
        axes[0,col].set_title(case['target'].removeprefix('confirmation-').capitalize())
        axes[1,col].axhline(0,color='black',lw=.6)
        axes[1,col].set(xlabel='Observation bin',xticks=np.arange(8)+.5,xticklabels=np.arange(1,9))
        for row in (0,1):
            axes[row,col].grid(alpha=.2)
            axes[row,col].spines[['top','right']].set_visible(False)
    axes[0,0].set_ylabel('Estimated dynamic power (mW)')
    axes[1,0].set_ylabel('Signed reference-mean error')
    fig.legend(*axes[0,0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,fontsize=8)
    fig.subplots_adjust(left=.12,right=.98,bottom=.19,top=.92,wspace=.26,hspace=.16)
    (figures / 'supplementary').mkdir(exist_ok=True)
    fig.savefig(figures/'supplementary/mesh_power_profiles.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tectonic", required=True, type=Path)
    parser.add_argument("--submission", action="store_true", help="Reject unresolved draft TODOs")
    parser.add_argument("--allow-overlength", action="store_true", help="Build an overlength working draft, never a submission")
    args = parser.parse_args()
    if args.submission and args.allow_overlength:
        parser.error('--allow-overlength cannot be used with --submission')
    tool = args.tectonic.resolve(strict=True)
    source = (PAPER / "report.tex").read_text()
    if any(mark in source for mark in ("\u2013", "\u2014", "--")):
        raise ValueError("Long dashes are not allowed in the paper source")
    if r"\documentclass[conference]{IEEEtran}" not in source:
        raise ValueError("Use the standard IEEE conference layout")
    if any(package in source for package in ('newtxtext', 'newtxmath', 'flushend', 'geometry')):
        raise ValueError("Keep the linked IEEE template's native typography and layout")
    acknowledgment = source.split(r"\section*{Acknowledgment", 1)
    if len(acknowledgment) != 2 or "AI" not in acknowledgment[1].split(r"\bibliograph", 1)[0]:
        raise ValueError("Hackathon requires acknowledgment of AI writing assistance")
    if args.submission and r"\todo{" in source:
        raise ValueError("Resolve visible TODOs before preparing the submission PDF")
    from agcws.reporting.mesh_sensitivity import verify as verify_mesh_sensitivity
    sensitivity_path = ROOT / 'results/mesh/sink-sensitivity'
    if verify_mesh_sensitivity(sensitivity_path) != json.loads((sensitivity_path/'summary.json').read_text()):
        raise ValueError('Regenerate the Mesh sensitivity summary from its evidence')
    subprocess.run([sys.executable, str(PAPER / "scripts/extract.py")], cwd=ROOT, check=True)
    render()
    pending_count = pending_table_cells(PAPER / "figures")
    if args.submission and pending_count:
        raise ValueError("Resolve pending table cells before preparing the submission PDF")
    output = ROOT / "out" / "paper-build"
    output.mkdir(parents=True, exist_ok=True)
    command = [str(tool), "--keep-logs", "--outdir", str(output), str(PAPER / "report.tex")]
    subprocess.run(command, cwd=ROOT, env={**os.environ, "SOURCE_DATE_EPOCH": "1789862400"}, check=True)
    log = (output / "report.log").read_text()
    if re.search(r"Overfull \\[hv]box|undefined references|Citation .* undefined", log):
        raise ValueError("Resolve TeX overflow or references before publishing the draft")
    info = subprocess.check_output(["pdfinfo", str(output / "report.pdf")], text=True)
    pages = int(re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE).group(1))
    if pages != 4 and not args.allow_overlength:
        raise ValueError(f"Hackathon paper must fit four total pages, got {pages}")
    shutil.copyfile(output / "report.pdf", PAPER / "report.pdf")
    paths = INPUTS + ["results/index.json", "src/agcws/evidence/catalog.py", "paper/scripts/build.py", "paper/scripts/extract.py", "paper/scripts/extract_strong.py", "paper/scripts/extract_power.py", "paper/evidence/figure_recipe.json",
                      "src/agcws/evidence/packs.py", "paper/report.tex", "paper/report.pdf",
                      "paper/figures/supplementary/matched_curves.pdf", "paper/figures/supplementary/matched_table.tex",
                      "paper/figures/final_table.tex", "paper/figures/supplementary/flash_efficiency.tex",
                      "paper/evidence/mesh_examples.json", "paper/figures/architecture.pdf",
                      "paper/figures/mesh_waveforms.pdf", "paper/figures/power_table.tex", "paper/figures/supplementary/mesh_power_profiles.pdf", "paper/references.bib"]
    power = json.loads((ROOT / INPUTS[4]).read_text())
    paths.extend(power['inputs'])
    paths.extend(['results/mesh/sink-sensitivity/evidence.json.gz',
                  'results/mesh/sink-sensitivity/summary.json',
                  'src/agcws/reporting/mesh_sensitivity.py',
                  'src/agcws/evaluation/power/mesh_sensitivity.py'])
    paths.extend(['src/agcws/reporting/redmule_validation.py',
                  'src/agcws/reporting/references.py',
                  'src/agcws/evidence/power.py',
                  'src/agcws/evaluation/power/windows.py',
                  'src/agcws/reporting/power_reference.py'])
    tasks = json.loads((PAPER / "evidence/task_vectors.json").read_text())
    paths.extend(["paper/evidence/task_vectors.json", "paper/evidence/task_vectors.md"])
    paths.extend(sorted({source["path"] for task in tasks.values()
                         for source in task["sources"].values()}))
    recipe = json.loads((PAPER / "evidence/figure_recipe.json").read_text())
    from agcws.evidence import packs
    strong = json.loads((ROOT / INPUTS[3]).read_text())
    for result in strong['designs'].values():
        archive = result['archive']
        paths.extend([f'{archive}/{packs.PACK}', f'{archive}/retained-cache.json.gz'])
        paths.extend(f'{archive}/{shard}' for shard in packs.manifest(catalog.resolve(ROOT, archive))['shards'])
    for archive in sorted({s["archive"] for s in recipe["sources"].values()}):
        paths.append(f"{archive}/{packs.PACK}")
        paths.extend(f"{archive}/{shard}" for shard in packs.manifest(catalog.resolve(ROOT, archive))["shards"])
    paths = sorted({str(catalog.resolve(ROOT, p).relative_to(ROOT)) for p in paths})
    receipt = {"pages": pages, "scope": "Manuscript with completed search, revised reference-power results, Ibex validation and fixed-finalist Mesh sensitivity. Provider liabilities are not verified bills.",
               "format": "IEEEtran conference, 10pt, letter; references included in four-page limit",
               "within_page_limit": pages <= 4,
               "overlength_draft": pages > 4,
               "template_url": "https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn",
               "requirements_url": "https://agentic-arch.org/hackathon.html#final-submission",
               "requirements_checked": "2026-09-20", "submission_ready": args.submission,
               "readiness_scope": "Manuscript build gates only; final author and submission-checklist review remains manual.",
               "inputs_and_outputs": {p: digest(ROOT / p) for p in paths},
               "tectonic_sha256": digest(tool), "command": command,
               "matplotlib_version": matplotlib.__version__,
               "todo_count": source.count("\\todo{"), "pending_table_cells": pending_count}
    (PAPER / "evidence/build_provenance.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Built {pages} pages. Remaining TODOs: {receipt['todo_count']}.")


if __name__ == "__main__":
    main()
