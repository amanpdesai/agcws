from pathlib import Path
from scripts.resolve_sv_sources import resolve

def test_aes_core_manifest_contains_required_packages():
    paths = {path.relative_to(Path.cwd()).as_posix() for path in resolve("aes_cipher_core")}
    assert any(path.endswith("aes_pkg.sv") for path in paths)
    assert any(path.endswith("aes_reg_pkg.sv") for path in paths)
    assert any(path.endswith("prim_util_pkg.sv") for path in paths)
    assert not any(path.endswith("lc_ctrl_token_pkg.sv") for path in paths)
