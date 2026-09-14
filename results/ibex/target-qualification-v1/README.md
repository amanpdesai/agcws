# Ibex target qualification v1 — incomplete bank

Both CPU panels completed 4,608 slots under the original frozen procedure:
phase-random and phase-GA, 256 proposals each per request, nine requests per split.
Development and confirmation each qualify activation and quiet interval (2/8
non-flat families). Neither separate flat control qualifies. Every other miss
is retained; this bank is not admitted to the full study.

Per-split archives include `qualification.json`, every proposal and compact
measurement evidence. The packer restored and hash-checked 38,452 development
and 38,682 confirmation files. This packaging check is not independent waveform
resimulation. The qualification analysis checks exact slot counts, frozen vectors,
cache/trial agreement and recalculated loss.

These failures are CPU witness-search outcomes, not new agent results or proof
that the requests are impossible. The historical Pro confirmation used a
different target bank and remains scoped to that bank.

For source-sensitive reproduction of this measurement inventory, use commit
`988fb61ce`; subsequent runtime changes are separately versioned.
