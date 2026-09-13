# Pulse-guided witness qualification v2

All 340 frozen proposals were replayed against the unchanged v1 target vectors.
Development: 0/8 non-flat requests and no control qualify. Confirmation: 4/8
non-flat requests qualify (activation, burst, quiet-interval, alternating); the
control fails. No predicted fit was used for admission.

The [frozen procedure](../../../docs/REDMULE_PULSE_WITNESS_V2.md) allows at most
432 proposals; omitted job counts are explicitly logged as unplaced by the
proposal algorithm, not declared physically impossible. The archive retains the
manifest, pulse inputs, freeze hashes, all real results and the complete per-target
qualification report. It was restored and byte-verified against the exported run.
This is not eight-profile readiness or a policy comparison.
