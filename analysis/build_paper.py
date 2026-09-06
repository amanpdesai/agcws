"""Build the draft and fail on wrong length or overflowing typesetting."""
import argparse
import importlib.metadata
import json
import os
import re
import subprocess
from pathlib import Path

from analysis.audit_windowed_archive import audit
from analysis.report_windowed_power import render
from validation.aes_gls import sha


def build(tool):
    tool = tool.resolve(strict=True)
    root = Path('paper')
    archive = Path('results/windowed_power_v1')
    audit(archive)
    render(archive,Path('docs/WINDOWED_POWER_RESULTS.md'),root)
    env = {**os.environ,'SOURCE_DATE_EPOCH':'1788652800'}
    command = [str(tool),'--keep-logs',str(root/'report.tex')]
    subprocess.run(command,env=env,check=True)
    metadata = subprocess.run(['pdfinfo',str(root/'report.pdf')],capture_output=True,text=True,check=True).stdout
    pages = re.search(r'^Pages:\s+(\d+)$',metadata,re.MULTILINE)
    if not pages or int(pages[1]) != 4:
        raise ValueError('draft is not four pages')
    if 'Overfull' in (root/'report.log').read_text():
        raise ValueError('typesetting overflow')
    words = []
    for page in range(1,5):
        content = subprocess.run(['pdftotext','-f',str(page),'-l',str(page),str(root/'report.pdf'),'-'],
                                 capture_output=True,text=True,check=True).stdout
        words.append(len(content.split()))
    if min(words) < 250:
        raise ValueError('unexpectedly sparse page; inspect layout')
    version = subprocess.run([str(tool),'--version'],capture_output=True,text=True,check=True).stdout.strip()
    paths = [root/'report.tex',root/'report.pdf',root/'window_profiles.pdf',root/'window_findings.tex',
             root/'window_figure_provenance.json',archive/'validation.json',Path('docs/LITERATURE.md'),Path(__file__)]
    record = {'pages':4,'page_word_counts':words,'overflow':False,'source_date_epoch':env['SOURCE_DATE_EPOCH'],
              'tool_version':version,'tool_sha256':sha(tool),'command':command,
              'tex_bundle_url':'https://data1b.fullyjustified.net/tlextras-2022.0r0.tar',
              'matplotlib_version':importlib.metadata.version('matplotlib'),
              'artifacts':{str(p):sha(p) for p in paths},
              'scope':'Working draft; not submission formatting, container verification, or an upstream PR.'}
    (root/'build_provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    print('FOUR_PAGE_DRAFT_VERIFIED',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tectonic',type=Path,required=True)
    args = parser.parse_args()
    build(args.tectonic)
