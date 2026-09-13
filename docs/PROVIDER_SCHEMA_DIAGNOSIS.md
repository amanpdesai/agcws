# Provider schema diagnosis

Mesh and RedMulE control smokes received HTTP 400 schema-complexity rejections
on both requested Flash calls. No generated response existed; these are API
failures, not model legality failures. Keep unknown usage and reserved liability,
not fabricated zero cost. Neither smoke passed readiness.

[Google's structured-output guidance](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output)
identifies long array limits and numeric constraints as possible complexity causes
and recommends reducing such constraints. The diagnostic tests a deliberately
projected provider grammar: retain types, property names, required fields, enums,
combinators and additional-property rules, but omit bounds/length/pattern
constraints from the serving grammar. The complete native schema remains in the
unchanged model payload and remains authoritative for local validation.

One metered Flash call per failed design, same first-call payload, two requested
slots; ceiling $0.20 each, no implicit retry or model fallback. Record original
and projected schemas, source and compiler hashes, raw output, usage and native
static checks. This isolates transport compatibility; no simulation or
end-to-end readiness is claimed from this diagnostic. Unknown requests cannot
be silently resampled.

Do not modify the live CPU studies' source tree to wire this into the main model
path while their frozen source inventories are in use. After a verified transport
fix is integrated under a new source fingerprint, rerun the bounded shared-loop
smokes. Historical rejected attempts remain separate.
