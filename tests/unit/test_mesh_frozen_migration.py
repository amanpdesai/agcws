import hashlib
from pathlib import Path

import pytest

from agcws.designs.mesh.frozen import original_harness, frozen_dependency_name


def test_basejump_relocation_is_exact_and_bounded():
    assert frozen_dependency_name('benchmarks/support/basejump_stl/bsg_noc/a.sv') == Path('third_party/basejump_stl/bsg_noc/a.sv')
    assert frozen_dependency_name('third_party/basejump_stl/a.sv') == Path('third_party/basejump_stl/a.sv')
    assert frozen_dependency_name('benchmarks/support/other/a.sv') == Path('benchmarks/support/other/a.sv')
    for name in ('/tmp/a.sv', 'benchmarks/support/basejump_stl/../a.sv'):
        with pytest.raises(ValueError, match='unsafe'):
            frozen_dependency_name(name)


def test_guard_migration_preserves_exact_frozen_bytes():
    current = Path("src/agcws/designs/mesh/assets/mesh_temporal.sv").read_bytes()
    original = original_harness(current)
    assert hashlib.sha256(original).hexdigest() == "13e5e91d8ec1f8c29046e42e0da1e61563d35425298d87b4354ac744ac76e7ba"
    assert original.startswith(b'`include "bsg_defines.sv"')
    assert b"AGCWS_MESH_MAPPED" not in original
    assert original.count(b"endmodule") == 2
    assert b"MESH_FUNCTIONAL_MISMATCH" in original
    # Changed functional bytes remain changed; inversion cannot conceal them.
    assert original_harness(current.replace(b"8192", b"8191")) != original


@pytest.mark.parametrize("change", [lambda b: b[1:], lambda b: b[:-1],
                                    lambda b: b.replace(b"`ifndef SYNTHESIS", b"`ifdef SYNTHESIS")])
def test_guard_migration_rejects_unrecognized_rewrites(change):
    current = Path("src/agcws/designs/mesh/assets/mesh_temporal.sv").read_bytes()
    with pytest.raises(ValueError, match="guard-only"):
        original_harness(change(current))
