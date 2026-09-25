# Paper

[Read the PDF](report.pdf) or edit [report.tex](report.tex).
Completed findings are summarized in [Results](../docs/RESULTS.md).

## Overleaf

Upload [overleaf.zip](overleaf.zip), select `main.tex`, and use pdfLaTeX.
Copy downloaded edits from `main.tex` back to `paper/report.tex`.

## Build

From the repository root:

```bash
.venv/bin/python paper/scripts/build.py --tectonic out/tools/tectonic-0.15.0/tectonic --submission
.venv/bin/python paper/scripts/overleaf.py
```

The build extracts archived data, generates figures and checks the four-page
limit. It makes no model calls or simulation runs. Logs stay in `out/paper-build/`.

| Folder | Contents |
| --- | --- |
| `scripts/` | Extraction, rendering, compilation and Overleaf packaging |
| `evidence/` | Figure recipe, extracted data, target vectors and build receipt |
| `figures/` | Plots and tables included in the manuscript |
| `figures/supplementary/` | Additional plots and tables |

Full experiment archives and aggregate summaries stay in `results/`.
