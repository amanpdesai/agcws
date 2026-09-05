# Semantic search development protocol

Development only: AES, targets 0.10/0.25/0.50/0.75/0.90, seeds 100–102,
50 proposal slots, batch size 4, epsilon 0.02 and the current AES activity
calibration. Compare random, evolutionary, and semantic-evolution-v2 with
identical budgets. All initialization proposals consume budget. V2 permits
one generation attempt per requested batch; malformed slots consume budget.

Primary endpoint: mean best-so-far error AUC. Secondary: solve rate, validity,
tokens and cost. This suite is for iteration, not confirmatory inference.
Hold out seeds 200–209 from development. Freeze implementation and prompt
before running that suite. Do not stop or select seeds based on performance.

Semantic v2 uses common random initialization followed by LLM mutations of
valid parents with compact signed feedback and explicit useful-work constraints.
Legacy Vertex results remain a separate experiment version. Coverage-guided
comparisons require measured coverage; activity diversity alone is not coverage.

V2 and compact-edit V3 probes (AES q=0.50, seed 100) produced MAX_TOKENS
responses and are diagnostic. V4 retains the V3 prompt, sets thinking_budget
to 512 and max_output_tokens to 8192, and counts reported thinking tokens as
output tokens. Previous cost estimates omitted thinking tokens and are incomplete.
V4 emits edits to existing scalar fields; this restricts its child representation
relative to full-workload generation and must be disclosed in comparisons.
The complete development suite is run before selecting a confirmatory policy.
