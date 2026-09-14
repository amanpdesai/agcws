# Late-feedback delivery diagnostic v1

2026-09-14, fixed before diagnostic calls. V5's strict sixteen-slot smoke
remains unchanged. DMA quiet-interval generated a valid candidate only in its
last batch; the short protocol therefore never delivered that measured result
to the model. This is not a reason to resample a seed or repeat the panel.

After each AES/DMA v5 smoke is complete, select **every** target that fails
measured-generated-feedback but has a valid generated candidate in slots 15–16.
Targets without any generated valid candidate are ineligible and remain
unready; do not substitute an initialization or witness. Freeze the selected
list and exact original sixteen-trial histories before executing anything.

Deliver each eligible history through the unchanged payload builder in exactly
one new two-slot call (slots 17–18). Use the same model, target, settings and
measurement runtime. Preserve the raw response, parse it and evaluate both
proposals with the ordinary evaluator. Charge both slots and all known or
unknown cost. No retries, repair, model substitution, seed search or extension
past this single call. At most eighteen calls per design, with a $2 ceiling
per design and one provider worker. Do not run comparative baselines: this is
a feedback-delivery diagnostic, not an extended policy comparison.

Pass requires the actual generated candidate and its measured rates/residual
to appear in the transmitted payload, a successful response from the pinned
model with known usage, exact accounting, and completed validation/evaluation
of both returned slots. It does not require solving or another valid proposal.
A failed delivery remains a failure; no automatic diagnostic rerun.

Report the sixteen-slot smoke as failed separately from a successful delivery
receipt. This can establish operational feedback wiring, not improved search
performance or reliable arithmetic compliance. Full-study inference excludes
all these engineering calls. Preserve every original archive.
