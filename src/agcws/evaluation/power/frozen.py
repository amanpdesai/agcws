"""Replay original measurement code without importing it into the release process."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from agcws.core import config
from agcws.core.provenance import file_sha256


def verify_sources(manifest, runtime):
    """Verify every original source at its recorded relative path."""
    runtime = runtime.resolve(strict=True)
    sources = manifest.get("sources")
    if not sources:
        raise ValueError("frozen replay requires a nonempty source inventory")
    mismatches = []
    for name, digest in sources.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe frozen source path: {name}")
        if path.parts[0] == ".dependencies":
            if not manifest["spec"]["domain"].startswith("redmule-temporal"):
                raise ValueError("unexpected external dependency inventory")
            # The frozen runner records the container mount name, not a host
            # checkout path. Verify its declared host source, byte for byte.
            dependency = config.path_setting("AGCWS_REDMULE_DEPS", "out/redmule-dependencies-v2")
            source = dependency.joinpath(*path.parts[1:])
        else:
            source = runtime / path
        if not source.is_file() or file_sha256(source) != digest:
            mismatches.append(name)
    if mismatches:
        raise ValueError(f"frozen source checkout differs: {mismatches[:10]}")
    return runtime


def replay(case, manifest, runtime, scratch):
    """Replay with the verified measurement runtime, including its simulator."""
    runtime = verify_sources(manifest, runtime)
    if (runtime / 'src/agcws/designs/temporal_registry.py').is_file():
        module = 'agcws.designs.temporal_registry'
    elif (runtime / 'src/agcws/pipeline/backends.py').is_file():
        module = 'agcws.pipeline.backends'
    else:
        raise ValueError('measurement runtime lacks a supported backend registry')
    if manifest['spec']['domain'].startswith('redmule-temporal'):
        if (runtime / 'out').is_symlink() or (runtime / '.dependencies').is_symlink():
            raise ValueError('RedMulE replay requires real container mount directories, not host symlinks')
        (runtime / 'out').mkdir(exist_ok=True)
        (runtime / '.dependencies').mkdir(exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=False)
    request = scratch / "replay-request.json"
    request.write_text(json.dumps({"case": case, "manifest": manifest}) + "\n")
    # Original Ibex measurement requires its exact precompiled simulator.
    binary_hash = manifest["runtime"].get("binary_sha256")
    if binary_hash:
        relative = Path("toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system")
        binary = Path(case["root"]) / relative
        if file_sha256(binary) != binary_hash:
            raise ValueError("frozen measurement binary differs")
        (scratch / relative).parent.mkdir(parents=True)
        shutil.copy2(binary, scratch / relative)
    command = (
        "import json,sys; from pathlib import Path; "
        f"from {module} import backend; "
        "root=Path(sys.argv[1]); req=json.loads((root/'replay-request.json').read_text()); "
        "result,hit=backend(req['manifest']['spec']['domain']).measured("
        "req['case']['program'],root,req['manifest']); "
        "(root/'replay-result.json').write_text(json.dumps(result)+'\\n')"
    )
    env = dict(os.environ, AGCWS_ROOT=str(runtime),
               PYTHONPATH=os.pathsep.join([str(runtime / "src"), str(runtime)]))
    if manifest['spec']['domain'].startswith('redmule-temporal'):
        env['AGCWS_REDMULE_DEPS'] = str(config.path_setting(
            'AGCWS_REDMULE_DEPS', 'out/redmule-dependencies-v2').resolve(strict=True))
    with (scratch / "replay.log").open("w") as log:
        subprocess.run([sys.executable, "-c", command, str(scratch.resolve())],
                       cwd=runtime, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = json.loads((scratch / "replay-result.json").read_text())
    if manifest["spec"]["domain"] == "ibex-temporal" and result["valid"]:
        # The original Ibex cache returns its measured rates inside profile;
        # its search-domain wrapper exposes that same vector at trial level.
        result = {**result, "rates": result["profile"]["window_rates"]}
    if not result["valid"] or result["rates"] != case["rates"]:
        raise ValueError("frozen functional replay differs from selected activity")
    receipt = {"runtime": str(runtime), "source_count": len(manifest["sources"]),
               "request_sha256": file_sha256(request),
               "result_sha256": file_sha256(scratch / "replay-result.json"),
               "rate_projection": "profile.window_rates" if manifest["spec"]["domain"] == "ibex-temporal" else "rates",
               "bridge_sha256": file_sha256(Path(__file__))}
    (scratch / "replay-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return result
