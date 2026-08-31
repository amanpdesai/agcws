# OpenTitan AES adapter

The pinned source is `third_party/opentitan`, with the AES IP under
`hw/ip/aes`. The production top level is the TileLink-connected `aes` module;
the harness must drive its TileLink request/response interface and provide
deterministic entropy, lifecycle, key-manager, and alert inputs.

The adapter's workload DSL remains transaction-level: configure key/mode,
submit blocks, optionally insert idle/backpressure intervals, and wait for
completion. The lower-level cipher core is useful for an isolated RTL smoke
test but is not the final workload interface.
