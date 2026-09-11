import hashlib
import json
import random
from pathlib import Path

import pytest

from agcws.pipeline.ibex.compiler import assembly
from agcws.pipeline.ibex.program import allocation, canonical, interpret, random_program
from agcws.pipeline.ibex.prompt import payload

GOLDEN = json.loads(Path("tests/fixtures/pipeline_legacy_golden.json").read_text())


@pytest.mark.parametrize("seed", range(100))
def test_consolidation_preserves_legacy_program_semantics(seed):
    program = random_program(random.Random(seed))
    data = {
        "program": canonical(program),
        "allocation": allocation(program),
        "reference": interpret(program),
        "assembly": assembly(program),
    }
    assert (
        hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        == GOLDEN["programs"][seed]
    )


def test_fixed_semantic_payload_matches_original():
    text = payload([], {"profile": [1] * 8, "scale": 100, "tolerance": 0.1}, 2, True)
    assert hashlib.sha256(text.encode()).hexdigest() == GOLDEN["payload"]
