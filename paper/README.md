# Four-page working report

[report.pdf](report.pdf) is an exactly four-page draft, not a submitted or
venue-formatted final paper. [report.tex](report.tex) is editable source.
All sixteen finalist profiles appear in [window_profiles.pdf](window_profiles.pdf);
the figure uses actual bin boundaries and nonzero vertical-axis ranges, not
invented zero-valued endpoints. Source data and renderer hashes accompany it.

## Build

Install the project's analysis dependencies. The local build used the official
Tectonic 0.15.0 x86_64 Linux musl binary, installed under ignored `out/tools/`.
[Official installation instructions](https://tectonic-typesetting.github.io/book/latest/installation/)
and [release](https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.15.0).

Release archive SHA-256:
`dfb82876f2986862996e564fa507a9e576e0c1e3bee63c2c1bd677c2543e6407`.
Executable SHA-256:
`4df19452c202c5bef9f7c7e4a01a3f2b9d5199f0a1f73b70b4fe1bffbc9837f6`.

```bash
.venv/bin/python -m analysis.audit_windowed_archive
.venv/bin/python -m analysis.build_paper --tectonic <tectonic-binary>
pdfinfo paper/report.pdf
```

The first Tectonic build downloads its TeX support bundle
`https://data1b.fullyjustified.net/tlextras-2022.0r0.tar`; later builds use cache.
No system-wide TeX installation, model calls, or EDA reruns are needed.
`build_provenance.json` records the actual binary, source, figure and PDF hashes.
PDF inspection must still check four pages and no overflow after edits.

## Before submission

- Author review and required venue formatting; affiliation and author list confirmation.
- Resolve remaining nearby-work checks in `docs/LITERATURE.md`, particularly FuzzPower.
- Complete a clean-container replay; current studies are explicitly host-run.
- Prepare the upstream contribution separately; no submitted PR is claimed.

Do not remove the negative results, conditional-analysis caveats, unknown-cost
flags, selected-finalist scope, or zero-delay limitation to make room.
