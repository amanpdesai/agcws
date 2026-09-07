# V4 response contract — serving-schema revision 2

Development-only revision after all 12 full-schema requests in Stage A returned
HTTP 400 (serving constraint too complex). Preserve that failed study at
`results/ibex_temporal_v4_contract/`. No response-generation result supports
choosing this revision; it addresses the explicit API rejection.

Repeat the same 12 contexts, both arms, counterbalanced order, 24 calls and 48
requested slots. Settings, prompts, complete schema in the payload, local
validator, parsing and accounting remain unchanged. The only change from the
first comparison is the schema sent in `response_json_schema`: collapse the
instruction union into an operation enum with optional operand fields and remove
array-length/numeric bounds from the server grammar. Local validation retains
all original requirements. Do not normalize forbidden extra fields or unwrap
programs. The full local schema, not the relaxed server grammar, defines validity.

The same readiness criterion applies: >=90% schema-valid requested candidates in
the contract arm, no API errors or unknown usage in that arm. Report both arms,
response adherence, missing/invalid slots, finishes, tokens and cost. This is
interface readiness on observed contexts, not temporal search or held-out evidence.
One attempt per call; no repair or substitution. A further failure requires a
new documented development decision, not an unrecorded retry. Commit the revised
manifest before requests.
