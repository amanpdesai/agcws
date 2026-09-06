# Literature review

## Verification legend

`[V]` verified against a primary source; `[P]` metadata confirmed but full text not read; `[U]` unverified secondary summary. No `[U]` entry may support a novelty claim.

## Novelty boundary

Prior work covers power viruses, stressmarks, extrema, switching maximization, low-power ATPG, and LLM hardware fuzzing for verification. This project studies goal-conditioned arbitrary scalar, compositional, and temporal power profiles over heterogeneous legal workload interfaces. This is a literature-supported gap, not an absolute-first claim.

## Outstanding verification

Read and verify FuzzPower first; then SAT/ILP maximum-power estimation and burn-in vectors, Deligiannis 2021, SAGA, and LLM-Box. Convert every `[U]` to `[V]`/`[P]` or remove it before the report.

## Sources used in the four-page draft — checked 2026-09-06

| Work | Primary evidence inspected | Status and permitted claim |
|---|---|---|
| Joshi, Eeckhout, John, Isen, *Automated Microprocessor Stressmark Generation*, HPCA 2008, 229–239, doi:10.1109/HPCA.2008.4658642 | [Author repository](https://biblio.ugent.be/publication/678619); [paper excerpt](https://citeseerx.ist.psu.edu/document?doi=44b022b30dbf890cfa3a403fe1b0c4eca1d9e4e3&repid=rep1&type=pdf) | [P] Abstract/first-page evidence of automated stressmark search; not an exhaustive full-text review. Repository page range conflicts with the actual paper beginning at 229; draft uses 229–239. |
| Chatzimiltis, Antoniou, Volos, Sazeides, *SAGA*, ISPASS 2025, 309–319, doi:10.1109/ISPASS64960.2025.00036 | [Authors' presentation](https://www.cs.ucy.ac.cy/carch/xi/ISPASS2025_Pres_1.pdf); [authors' tool page](https://www8.cs.ucy.ac.cy/ResearchLabs/carch/xi/saga_tool.php) | [P] Surrogate-assisted GA targets CPU power viruses. Full paper not read; draft does not borrow quantitative speedup claims. |
| Cui et al., *CHIA*, arXiv:2606.27350v3 | [Primary abstract](https://arxiv.org/abs/2606.27350v3) | [P] Composable cyclic tool/model graphs and research infrastructure. Does not establish that our studies ran through CHIA/Ray. |
| OpenSTA, a9a3f30ca97dc13f9ef911cae1a82c42c67379e1 | [Pinned source](https://github.com/The-OpenROAD-Project/OpenSTA/tree/a9a3f30ca97dc13f9ef911cae1a82c42c67379e1), local `Power.tcl`, `VcdReader`, `Power.cc`, `PowerClass.hh`, upstream native-window regression | [V] Native bounds, activity handling and float32 power accumulation were inspected and independently exercised. |

Targeted searches did not locate a verifiable primary FuzzPower thesis record
in this pass. This does not establish nonexistence. Its title, artifact and
claimed objectives remain [U]; they are not used to support the draft's novelty
claims. The draft makes no absolute-first or exhaustive literature-gap claim.
Resolve this and the other outstanding nearby work before submission.
