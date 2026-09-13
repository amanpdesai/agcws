# Qualified-control Flash smoke v1

Initial paid plumbing checks on mesh and RedMulE, only after each confirmation
flat control passes exact replay in witness-refinement-v4. This is a subset of
readiness, not a full study or a substitute for non-flat-target smokes.

Per design: one control, seed 8200, policies flash-4096, phase-random, phase-GA,
six proposal slots per arm, batch size two. The first two proposals are shared
random initialization; Flash then makes two calls with measured history, so the
second call can receive feedback on its own first proposals. Disable early
stopping here to exercise that path even if the control is solved immediately.
Early-stop correctness remains a separate test and full-study setting.

Use the current pinned Flash-4096 settings and cost meter, three concurrent cells
and one provider worker per design. Cost ceiling $1 per design. No implicit model
substitution or retries. Provider failures, unknown usage, schema rejections and
missing feedback must be recorded, not called successful plumbing. Check payload
history, requested-slot accounting, real simulator results, tokens/cost/model and
cached resume. No witness programs or calibration programs enter model context.

Freeze configuration and qualification receipt before launching. Preserve every
attempt. These development smoke seeds will not be full-study seeds.
