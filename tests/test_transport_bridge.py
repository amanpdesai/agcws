import hashlib
import runpy
import subprocess

import pytest


def test_transport_bridge_rejects_measurement_and_unrelated_edits():
    module = runpy.run_path("analysis/transport_bridge.py")
    old = subprocess.check_output(["git", "show", f"{module['BASE']}:{module['MODEL']}"])
    new = subprocess.check_output(["git", "show", f"3ac647a65:{module['MODEL']}"])
    inventory = {module["MODEL"]: hashlib.sha256(old).hexdigest(), "measurement.py": "same"}
    current = {**inventory, module["MODEL"]: hashlib.sha256(new).hexdigest()}
    module["check_sources"](inventory, current, old, new)
    with pytest.raises(ValueError, match="model-only"):
        module["check_sources"](inventory, {**current, "measurement.py": "changed"}, old, new)
    with pytest.raises(ValueError, match="beyond transport"):
        module["check_sources"](inventory, current, old, new.replace(b'"temperature": 0.7', b'"temperature": 0.1'))


def test_transport_bridge_rejects_model_migration():
    module = runpy.run_path("analysis/transport_bridge.py")
    old = subprocess.check_output(["git", "show", f"{module['BASE']}:{module['MODEL']}"])
    new = (module["ROOT"] / module["MODEL"]).read_bytes()
    with pytest.raises(ValueError, match="beyond transport"):
        module["check_sources"]({module["MODEL"]: hashlib.sha256(old).hexdigest()},
                                {module["MODEL"]: hashlib.sha256(new).hexdigest()}, old, new)
