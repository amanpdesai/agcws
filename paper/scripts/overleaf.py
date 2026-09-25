"""Package the compiled draft and its static dependencies for Overleaf."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

TEMPLATE = 'https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn'
INSTRUCTIONS = '''# Overleaf project

Upload this ZIP using New Project > Upload Project.
Set the main document to main.tex and the compiler to pdfLaTeX.
IEEEtran and the standard LaTeX packages are supplied by Overleaf.
Click Recompile. No Python, simulation tools, shell escape, or result archives
are required. References are in references.bib, formatted with IEEEtran BibTeX.

Edit main.tex directly. The figures are static PDFs with repository-verified
measurement inputs; do not edit their numbers by hand.
Check author details before submission.

The manuscript uses the official IEEE conference template:
''' + TEMPLATE + '''

The canonical repository source is paper/report.tex, renamed main.tex only in
this upload bundle. SOURCE_MANIFEST.json records the packaged file hashes.
To regenerate figures, use the repository's paper/scripts/build.py, then overleaf.py.
After editing in Overleaf, download the source and bring main.tex back as
paper/report.tex before regenerating this bundle. Do not maintain two diverging
manuscripts. The four-page hackathon limit includes references and figures.
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dependencies(paper):
    paper = paper.resolve(strict=True)
    pending, files = [paper / 'report.tex'], {}
    while pending:
        path = pending.pop().resolve(strict=True)
        relative = path.relative_to(paper).as_posix()
        if relative in files:
            continue
        files[relative] = path.read_bytes()
        if path.suffix != '.tex':
            continue
        text = re.sub(r'(?<!\\)%.*', '', files[relative].decode())
        for command, name in re.findall(
                r'\\(includegraphics|input|include|bibliography)(?:\[[^\]]*\])?\{([^}]+)\}', text):
            for entry in name.split(',') if command == 'bibliography' else [name]:
                child = paper / entry.strip()
                if child.suffix == '':
                    if command == 'includegraphics':
                        raise ValueError('Use explicit figure extensions for portable packaging')
                    child = child.with_suffix('.bib' if command == 'bibliography' else '.tex')
                child.resolve(strict=True).relative_to(paper)
                pending.append(child)
    return files


def package(paper, output):
    files = dependencies(paper)
    build = json.loads((paper / 'evidence/build_provenance.json').read_text())
    for name, data in files.items():
        if build['inputs_and_outputs'].get(f'paper/{name}') != digest(data):
            raise ValueError(f'Rebuild the paper before exporting changed input: {name}')
    files['main.tex'] = files.pop('report.tex')
    files['README.md'] = INSTRUCTIONS.encode()
    if build['pages'] > 4:
        files['README.md'] += (f"\nWARNING: This working draft is {build['pages']} pages, exceeding the "
                               "four-page submission limit. Shorten it before submission.\n").encode()
    manifest = {'template': TEMPLATE, 'main_document': 'main.tex', 'compiler': 'pdfLaTeX',
                'pages_in_local_build': build['pages'], 'todo_count': build['todo_count'],
                'files': {name: digest(data) for name, data in sorted(files.items())}}
    files['SOURCE_MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    temporary.replace(output)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1] / 'overleaf.zip')
    args = parser.parse_args()
    manifest = package(Path(__file__).resolve().parents[1], args.out)
    print(json.dumps({'zip': str(args.out), 'files': len(manifest['files']) + 1,
                      'main': manifest['main_document']}))


if __name__ == '__main__':
    main()
