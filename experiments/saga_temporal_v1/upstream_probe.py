"""Exercise pinned upstream curve fitting in an isolated numerical environment."""

import contextlib
import hashlib
import importlib.util
import io
import json
import math
import sys
import warnings
from pathlib import Path

import numpy
import scipy


def main():
    path = Path("third_party/gest_saga/src/PredictReferenceFeatures.py")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != "6494ac6de7958b5ddf3b5cf3bf915c25b324214c898c3f0ecd8c4ff267132cfd":
        raise ValueError("upstream predictor changed")
    spec = importlib.util.spec_from_file_location("pinned_saga_predictor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [[float(i), 2 + 3 * math.log(i)] for i in range(1, 7)]
    positive = module.getReferenceFeatures([rows, ["known_log_feature"]])
    expected = 2 + 3 * math.log(106)
    if not math.isclose(float(positive[0][0][0]), expected, rel_tol=1e-7):
        raise ValueError("upstream positive-input fit differs")
    captured = io.StringIO()
    with (
        warnings.catch_warnings(record=True) as caught,
        contextlib.redirect_stdout(captured),
    ):
        warnings.simplefilter("always")
        negative = module.getReferenceFeatures(
            [[[-r[0], r[1]] for r in rows], ["known_log_feature"]]
        )
    result = {
        "predictor_sha256": digest,
        "python": sys.version.split()[0],
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "positive_prediction": float(positive[0][0][0]),
        "positive_expected": expected,
        "negative_input_output": float(negative[0][0][0]),
        "negative_input_warnings": sorted({str(w.message) for w in caught}),
        "negative_input_stdout": captured.getvalue(),
        "scope": "synthetic predictor contract only; no simulator or power-virus reproduction",
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
