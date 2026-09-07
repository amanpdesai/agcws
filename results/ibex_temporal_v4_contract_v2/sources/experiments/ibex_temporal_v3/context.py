"""Fixed source-context treatment, with retrieval receipts and no repository shell."""

from agcws.policies.source_context import SourceReader

CHAR_BUDGET = 24000
EXCERPTS = (
    ("specs/ibex.md", 1, 56),
    ("third_party/ibex/examples/simple_system/rtl/ibex_simple_system.sv", 1, 72),
    ("third_party/ibex/examples/simple_system/rtl/ibex_simple_system.sv", 303, 316),
    ("third_party/ibex/rtl/ibex_core.sv", 184, 203),
    ("third_party/ibex/rtl/ibex_cs_registers.sv", 1891, 1910),
    ("third_party/ibex/rtl/ibex_multdiv_fast.sv", 408, 529),
    ("third_party/ibex/rtl/ibex_load_store_unit.sv", 420, 486),
    ("third_party/ibex/rtl/ibex_load_store_unit.sv", 533, 545),
)


def load_context(root, digest):
    reader = SourceReader(root, digest, max_chars=CHAR_BUDGET)
    excerpts = [reader.read(*request) for request in EXCERPTS]
    return {
        "bundle_sha256": digest,
        "retrieval_character_budget": CHAR_BUDGET,
        "retrieved_characters": CHAR_BUDGET - reader.remaining,
        "excerpts": excerpts,
        "scope": "fixed supplied source context; retrieval does not prove comprehension",
    }
