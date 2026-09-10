# Upstream baselines and temporal confirmation

2026-09-10. Living roadmap; does not amend any frozen experiment.

## Direction and current evidence

The objective is finite-budget temporal target discovery against credible search
controls, not proving that one policy has a more expressive language. Every arm
must share a documented legal workload space. Ibex is the current development
design. Targets are RTL activity rates, not watts; Ibex gate-power validation
and cross-design transfer remain separate requirements.

The completed Pro depth study is promising development evidence, not held-out
confirmation. The temporal-scaling qualification implemented request generation,
witness checks, phase-random and phase-GA, but did not establish stronger-baseline
efficacy or qualify the synthetic requests as a harder benchmark. Longer horizons
and additional bins still need a versioned measurement implementation.

## Stages

1. **Upstream integration qualification (first slice, CPU only).** Inspect and
   pin official GeST and GeST-SAGA sources. Verify notices, dependencies,
   representation, selection/mutation and surrogate training/measurement paths.
   Identify a bounded interface into our evaluator and test upstream components
   without executing supplied remote-machine measurement scripts. Record actual
   incompatibilities and whether an adaptation is necessary.
2. **Unchanged Pro confirmation.** Freeze the dedicated protocol described in
   `TEMPORAL_SCALING_V1_PLAN.md`: fresh seeds, original four targets, original
   random versus Pro-4096, 128 slots. Check cumulative spend and liability cap
   before calls. Upstream integration must not alter this comparison.
3. **Balanced target construction and stronger-control development.** Construct
   witnesses with several generators; retain failures, freeze selection rules
   independently of policy outcomes, and withhold witness programs. Compare Pro,
   original random, phase-random, phase-GA and qualified upstream adaptations.
   Select baseline configurations on development data only.
4. **Scale and confirm generalization.** Thread duration and resolution through
   a new evaluator with legacy equivalence and exact-count gates. Qualify longer
   and higher-resolution requests before freezing fresh targets and search seeds.
   Change duration, resolution and amplitude separately before crossing them.

## Official artifacts

- [GeST](https://github.com/toolsForUarch/GeST): original ISPASS 2019 framework.
  The detailed `README` contains the permission notice, Python/XML configuration
  and custom measurement/fitness extension guidance; examples are ARM/x86.
- [GeST-SAGA](https://github.com/ucy-xilab/GeST-SAGA): linked by the
  [authors' SAGA tool page](https://www8.cs.ucy.ac.cy/ResearchLabs/carch/xi/saga_tool.php)
  through its former `ucy-xilab/GeST` URL. The repository describes its surrogate
  extension; inspect code before claiming faithful algorithm reproduction.
- [HPCA 2026 temporal stressor paper](https://lca.ece.utexas.edu/pubs/jiang_hpca26.pdf):
  no verified public code repository located in the current search. This is an
  unresolved artifact search, not evidence that code does not exist.

Use immutable upstream commits, preserve notices, and keep adaptations outside
read-only source trees. A published algorithm adapted to RISC-V and temporal
loss must be named an adaptation, with the changes enumerated. Our existing
phase-GA is not GeST or SAGA.

## Accounting and comparison contract

The primary existing endpoint remains AUC over proposed candidates. Invalid
candidates, duplicates and initialization slots count; no silent repair or
policy fallback. Real measurements alone enter the measured best-so-far archive.
Surrogate predictions are explicitly distinguished from evaluator observations.

For SAGA, additionally count internally generated candidates, surrogate scores,
training observations, actual simulator calls and wall-clock cost. Predeclare
where a proposal enters the public budget; do not conceal candidate filtering.
Include a separately labeled equal-simulator-call view to measure surrogate
savings. Do not change the frozen studies' primary budget retrospectively.

Upstream hardware measurement commands, SSH credentials, sudo configuration and
power-meter setup are not appropriate for our simulator bridge. Do not execute
those examples or weaken host permissions to make them run.

## First-slice acceptance

- Exact upstream revisions and permission locations recorded.
- Concrete code-level map of representation, operators, fitness, surrogate and
  measurement entry points, with integration hazards documented.
- A bounded CPU-only component test or explicit evidence-backed incompatibility
  report; no paid study or hardware stress loop launched.
- Integration checklist covering shared language support, invalid handling,
  reproducibility, budget charging and surrogate training isolation.
- Tracked documentation and tests; no changes to historical frozen sources.

This slice qualifies the integration route. It does not deliver an entire
RISC-V port, an upstream-baseline matrix, or a new superiority claim.
