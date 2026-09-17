# Model answer-visibility audit — 2026-09-16

Offline audit of the published Ibex all-bin pilot and local Gemini 3 AES migration
smoke. No model calls, simulations, runtime changes or baseline restarts.
[Machine-readable checks](audit.json) include input archive and response hashes.

## Finding

No direct hidden-answer path was found in the inspected requests. This is a
bounded dataflow check, not a universal no-leakage certification or proof of
semantic reasoning. Existing studies and future runs require their own audits.

### Ibex all-bin pilot

- 1,667 archive members checksum-verified; 82 saved payloads (79 with saved
  responses) reconstructed byte-for-byte. A saved input alone is not proof a
  provider call was made: the cost gate can stop after input persistence.
- 527 displayed history rows matched prior trials of the same cell. All payload
  fields, including omitted-history selection and 468 notebook notes, reconstructed
  from that history and the public goal. Scorable notebook direction/delta values
  were also recomputed independently of the notebook implementation.
- 16 initial programs regenerated from seeds alone and matched across arms.
  No target-conditioned witness initialization was found.
- 79 provider responses decoded back to proposals; proposal/trial correspondence
  and request identities checked. 678 trial records inspected, including 677
  cache-backed records. Cache keys bind the submitted canonical program and frozen
  measurement identity. Rates and execution/feedback records match those caches.
- No canonical whole-program matches to any of the 216 archived measured-mixture
  witness candidates, either in proposals or displayed history. No complete
  segment/opcode-shape matches either; this secondary structural check is deliberately
  narrow and does not rule out reuse of individual instruction motifs.
- Context, program, notebook and schema reconstruction sources match their frozen
  source hashes. This does not certify every historical runtime source or binary.

### AES migration smoke

All four inputs reconstruct from the generic AES context, public target, and
that model's own prior trial. Both models received byte-identical first payloads
with empty histories. Each second request included only its own first trial.
All four simulations were cache misses; provider programs match the canonical
programs evaluated and recorded rates match their cached measurements.

Comparison against 27 canonical AES refinement programs found **one overlap**:
Lite's first proposal is eight repetitions of work(8), wait(750). This common
equal-allocation pattern did not solve the requested target. Neither strong-model
proposal matches these archived programs. Exact equality is a diagnostic, not
proof of leakage: simple bounded grammars admit independently identical programs.

The strong model's first successful program repeats wait(1500), work(16) four
times. The public contract supplies 6,000 idle cycles and 64 blocks, and the target
supplies four alternating active regions. This arithmetic is sufficient to suggest
that program without a reference solution. Its success is therefore compatible
with straightforward schedule construction, not necessarily deep RTL understanding.

## Boundary and limitations

Allowed: requested bin values, units/normalization, success rule, workload schema,
generic hardware behavior and exact budgets, and prior same-cell measured feedback.
Forbidden: hidden witness programs, witness measurements beyond the requested
target, constructor probe tables, other cells' trial histories, future feedback,
or replacement of a provider's proposal with a known solution.

The inspected API transport supplies explicit text and a generic response schema;
it does not enable retrieval, filesystem tools, or a server-side conversation.
The simulation subprocess has repository access, but is not the LLM. The measured
cache can reuse an identical submitted workload; it does not choose proposals or
offer a best-solution lookup. Current code inspection supports these statements;
there is no independent provider-side network capture in this audit.

Shared phase vocabulary and useful hardware hints remain a **mechanism confound**,
not demonstrated answer leakage. Generic context can make a task much easier.
Prior exposure of the pilot target/seeds also prevents calling this held-out.
Neither point is erased by clean payload lineage. Independent target families,
context/feedback ablations, and matched capable baselines are still needed for
claims about semantic understanding or broad superiority.

This audit does not independently resimulate waveforms, inspect model training
data, certify all older studies, or establish cycle-wise tracking. Witness matching
covers only the named Ibex and AES banks. Migration inputs remain local scratch;
their hashes are recorded, but this report alone does not make them portable.

## Reproduction

From the repository root, with the migration scratch records present:

```sh
.venv/bin/python -m analysis.audit_model_visibility --output /tmp/model-visibility-audit.json
.venv/bin/pytest -q tests/test_model_visibility_audit.py tests/test_solution_audit.py
```

Negative tests inject future/cross-cell program or rate content, forged notebook
deltas, hidden goal fields, and altered archive bytes. All must be rejected.
