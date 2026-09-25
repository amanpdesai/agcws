"""Read-only contract comparison for the frozen Flash matched study.

Paths below are identifiers in published manifests, not active source locations.
Preparation uses the shared study CLI; the historical launcher is retired.
"""

from agcws.search.providers.gemini import settings

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")
ARM = "flash-lite-medium"
PROVIDER_ONLY = {"src/agcws/pipeline/model.py", "src/agcws/pipeline/schedule_backend.py"}
CONFIG_CHANGES = {"name", "policies", "cost_ceiling_usd"}


def matched(reference, candidate, arm=ARM):
    for field in set(reference["spec"]) | set(candidate["spec"]):
        if field not in CONFIG_CHANGES and reference["spec"].get(field) != candidate["spec"].get(field):
            raise ValueError(f"task contract changed: {field}")
    for field in ("schema", "runtime"):
        if reference[field] != candidate[field]:
            raise ValueError(f"{field} changed")
    changed = {p for p in reference["sources"].keys() | candidate["sources"].keys()
               if reference["sources"].get(p) != candidate["sources"].get(p)}
    if changed - PROVIDER_ONLY:
        raise ValueError(f"non-provider sources changed: {sorted(changed - PROVIDER_ONLY)}")
    if candidate["spec"]["policies"] != [arm] or candidate["models"] != {arm: settings(arm)}:
        raise ValueError("unexpected model arm or settings")
    return {p: {"baseline": reference["sources"][p], "flash": candidate["sources"][p]}
            for p in sorted(changed)}
