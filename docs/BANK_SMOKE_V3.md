# Fixed corrective-feedback smoke v3

The six-slot v2 test exposed exact-resource violations, not provider transport
failures. Its requirement that the *first* generated batch be valid conflates
schema/protocol reliability with whether a closed loop can use corrective
feedback. Do not erase those failures or call the model fully reliable.

Run one declared follow-up on every admitted AES/mesh/DMA request, not only the
failures: seed 8501, 16 slots, batches of two, the same Flash-4096, phase-random
and phase-GA, same schemas, prompt, targets, calibration and hard validity gates.
No model, prompt or evaluator change. Eighteen cell workers, three provider
workers, $12 reservation cap per design. Disable early success stopping for
this feedback test only. Seven model calls per target maximum; no retries or
extra seeds. Stop after this panel irrespective of results.

Readiness requires at least one valid model-generated workload to appear in a
later model call's exact measured history for each target, all calls to have
known usage and expected model identity, and accounting/cache checks to pass.
A model receiving a validation error is useful corrective feedback but does
not alone satisfy the measured-feedback requirement. Report first-batch and
all-generated validity separately. This longer test is not an improvement in
the model or a policy result. Never select or combine favorable seeds for paper
inference; both smoke seeds are excluded from that study.
