# CHIA flows

Flows are the only layer that knows how generic nodes are wired into a CHIA
loop. Keep design logic in adapters and experiment choices in `experiments/`.

The intended task graph is:

```text
propose -> validate -> elaborate -> simulate -> activity -> power -> loss -> ledger
                                                   |
                                      periodic finalist synthesis is cached
```

Each candidate consumes proposal budget before validation. The reusable
`flows.chia_nodes` surface exposes CHIA-decorated simulation, activity, and
strict OpenSTA power nodes; experiment-specific proposal and loss logic stays
outside that surface. Synthesis is cached per design and is never part of the
inner-loop budget.
