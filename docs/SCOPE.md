# Scope

**Project:** Agentic Goal-Conditioned Workload Synthesis for Dynamic Power Characterization  
**Venue:** A³ CHIA Hackathon (MICRO 2026)  
**Build window:** 2026-08-29 (D1) through 2026-09-20 (D23)  
**Status:** FROZEN after D3; changes require an entry in `DECISIONS.md`.

## Research question

Given an RTL design, a legal stimulus interface, and a target dynamic-power profile, can an agent synthesize semantically valid workloads that drive the design toward that behavior?

## Deliverables

- Open-source CHIA loop, three adapters (Ibex, OpenTitan AES, verilog-axi `axi_dma`), and reproducible container.
- Verilator/activity inner-loop with Yosys/OpenSTA validation.
- Random, mutation, evolutionary, one-shot LLM, and hybrid baselines.

## Scope and claim discipline

Scalar targets span all designs; compositional targets focus on Ibex/AES; coarse temporal targets focus on AES/`axi_dma`. FireSim, commercial tools/PDKs, cross-PDK transfer, learned evaluator routing, per-cycle profiles, a fourth design, RTL modification, and signoff claims are out of scope. The novelty claim is arbitrary goal-conditioned profiles across heterogeneous interfaces, not the first power-virus generator. Unless Liberty is fully characterized, report synthesis-weighted switching power.
