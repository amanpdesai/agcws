# CHIA flows

Flows are the only layer that knows how generic nodes are wired into a CHIA
loop. Keep design logic in adapters and experiment choices in `experiments/`.

The intended task graph is:

```text
propose -> validate -> elaborate -> simulate -> activity -> loss -> ledger
                                                   |
                                      periodic finalist synthesis/power
```

Each candidate consumes proposal budget before validation. Synthesis is cached
per design and is never part of the inner-loop budget.
