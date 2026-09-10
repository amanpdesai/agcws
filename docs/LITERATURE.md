# Literature review

## Verification legend

`[V]` verified against a primary source; `[P]` metadata confirmed but full text not read; `[U]` unverified secondary summary. No `[U]` entry may support a novelty claim.

## Novelty boundary

Prior work covers power viruses, stressmarks, extrema, switching maximization,
low-power ATPG, LLM hardware fuzzing, and **controlled periodic current/power
waveforms for dI/dt stress**. Shaped temporal workload generation is established.
This project evaluates requested profile matching under shared legal interfaces
and proposal budgets. Arbitrary/nonperiodic profile tracking and cross-interface
controllers are evaluation questions, not an established absolute-first claim.
Custom fitness functions in prior systems may also express vector errors; merely
accepting a target vector does not itself establish novelty.

## Temporal stress literature — primary-source pass, 2026-09-09

| Work | Evidence and verification scope | Consequence |
|---|---|---|
| Jiang et al., *Exploration of LLM Workload Reliability based on di/dt Effects and Voltage Droops*, HPCA 2026 | [Author PDF](https://lca.ece.utexas.edu/pubs/jiang_hpca26.pdf), abstract and §V.A–F inspected. [V] for these method statements, not reproduction: GPU knob-based code generation; timer-controlled high/low phases; GA mixed-parameter crossover/mutation; separate PDN analysis. | Periodic temporal control is prior art. Adapt the separation of representation, generator and search, not its GPU-specific constants. The paper's LLMs are workloads under test, not a semantic workload-generating agent. |
| Kim and John, *Automated di/dt Stressmark Generation for Microprocessor Power Delivery Networks*, ISLPED 2011, doi:10.1109/ISLPED.2011.5993645 | [Author PDF](https://lca.ece.utexas.edu/pubs/young_islped11.pdf), abstract and §§I–IV inspected; [V] for periodic high/low current and GA sequencing/register/dependency controls. [Author publication list](https://lca.ece.utexas.edu/pubs-by-date.php) confirms 2011; the supplied ResearchGate venue metadata inconsistently says 2010. | Temporal scheduling and dependencies are established optimization dimensions. No voltage-droop claim follows from our activity-rate measurements. |
| Hadjilambrou, Das, Whatmough, Bull, Sazeides, *GeST: An Automatic Framework For Generating CPU Stress-Tests*, ISPASS 2019 | [Upstream README](https://github.com/toolsForUarch/GeST), [paper](https://ieeexplore.ieee.org/document/8695639/). [P] Title/authors/venue confirmed. Supplied [author PDF](https://www5.cs.ucy.ac.cy/carch/xi/papers/ISPASS_2019_for_webpage.pdf) was inaccessible (TLS/fetch errors); full algorithm and specified-frequency capability not verified in this pass. | Relevant framework to inspect for a direct baseline. Do not call our new phase-GA a reproduction or repeat unverified configuration claims. |
| Hadjilambrou, Das, Antoniades, Sazeides, *Harnessing CPU Electromagnetic Emanations for Resonance-Induced Voltage-Noise Characterization*, IEEE TC 2021, doi:10.1109/TC.2020.3008851 | [Authors' publication index](https://www8.cs.ucy.ac.cy/ResearchLabs/carch/xi/publications.php), [publisher link](https://dl.acm.org/doi/10.1109/TC.2020.3008851). [P] Metadata confirmed by indexed author listing; publisher full text blocked. Four-CPU experimental and exact search claims from the supplied summary remain unverified. | Review EM-guided fitness and resonance characterization before citing quantitative results. |
| Chatzimiltis et al., *SAGA*, ISPASS 2025 | [Author tool listing](https://www8.cs.ucy.ac.cy/ResearchLabs/carch/xi/saga_tool.php), [publisher](https://ieeexplore.ieee.org/document/11096384/). [P] Surrogate-assisted CPU power-virus GA, also noted below. Full paper unavailable in this pass; no borrowed speedup claim. | Surrogate-assisted phase search is a candidate stronger baseline, not implemented or reproduced by this milestone. |

The implementation plan is [TEMPORAL_SCALING_V1_PLAN.md](TEMPORAL_SCALING_V1_PLAN.md).
It does not require downloading prior code into the project or copying paper
figures/text. The research audit must finish inaccessible full-text reviews
before claiming exhaustive coverage of temporal synthesis methods.

## Outstanding verification

Artifact discovery update, 2026-09-10: the authors' SAGA tool page links
`ucy-xilab/GeST`, which redirects to the official
[GeST-SAGA repository](https://github.com/ucy-xilab/GeST-SAGA).
The [original GeST repository](https://github.com/toolsForUarch/GeST) is also
available. Repository identity and setup documentation are verified; algorithm
reproduction and RISC-V compatibility are not. See the
[integration roadmap](UPSTREAM_BASELINES_PLAN.md). Earlier notes about unavailable
full papers do not mean these code artifacts are unavailable.

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

## AgentDSE — checked 2026-09-07

[V] Wang et al., *AgentDSE: Reasoning-Augmented Architectural Design Space
Exploration*, arXiv:2606.21836v1. [Primary paper](https://arxiv.org/pdf/2606.21836).
Full text read; reported experiments not independently reproduced.
See [research assessment](RESEARCH_DIRECTION.md) for proposed adaptations.
