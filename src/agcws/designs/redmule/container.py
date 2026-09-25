"""Explicit host/container boundary for the matched RedMulE GLS recipe."""

import json
import os
import subprocess
from pathlib import Path

from agcws.core import config
from agcws.designs.redmule.gls import sha
from agcws.evaluation.waveforms.reference_clock import reference_clock_vcd


def container_path(path):
    return Path('/workspace') / Path(path).resolve().relative_to(config.ROOT)


def invoke(code, arguments):
    image = os.environ.get('AGCWS_REDMULE_GLS_IMAGE', 'agcws:benchmark-v1')
    image_id = subprocess.check_output(
        ['docker', 'image', 'inspect', '--format', '{{.Id}}', image], text=True).strip()
    env = dict(os.environ, AGCWS_CONTAINER_IMAGE=image_id,
               AGCWS_CONTAINER_OUTPUT=str(config.ROOT / 'out'),
               AGCWS_CONTAINER_DEPS=str(config.path_setting(
                   'AGCWS_REDMULE_DEPS', 'out/redmule-dependencies-v2').resolve(strict=True)))
    command = ['bash', str(config.ROOT / 'docker/run.sh'), 'env',
               'AGCWS_SKY130_CELL_MODELS=/usr/local/share/agcws/sky130_hd.v',
               'AGCWS_SKY130_PRIMITIVES=/usr/local/share/agcws/sky130_hd_primitives.v',
               'AGCWS_VERILATOR=/workspace/src/agcws/evaluation/simulation/cached_verilator.py',
               f'AGCWS_GLS_IMAGE_ID={image_id}',
               f"AGCWS_REDMULE_GLS_JOBS={os.environ.get('AGCWS_REDMULE_GLS_JOBS', '2')}",
               'python3', '-c', code, *map(str, arguments)]
    subprocess.run(command, env=env, check=True)
    return image_id


def verify_synthesis(synthesis):
    invoke('import json,sys; from pathlib import Path; '
           'from agcws.evaluation.power.finalists import verify_synthesis_sources; '
           'from agcws.designs.redmule.gls import verify_preparation; '
           'p=Path(sys.argv[1]); verify_preparation(p); '
           'verify_synthesis_sources(json.loads((p/"manifest.json").read_text()))',
           [container_path(synthesis)])


def replay_trial(rtl, synthesis, out, *, frozen_receipt=None):
    arguments = [container_path(p) for p in (rtl, synthesis, out)]
    arguments.append(str(container_path(frozen_receipt)) if frozen_receipt else '')
    image_id = invoke(
        'import sys; from pathlib import Path; '
        'from agcws.designs.redmule.matched import replay_trial; '
        'replay_trial(*map(Path,sys.argv[1:4]), '
        'frozen_receipt=Path(sys.argv[4]) if sys.argv[4] else None)', arguments)
    result = json.loads((out / 'matched_replay.json').read_text())
    for key in ('waveform', 'rtl_waveform', 'receipt'):
        relative = Path(result[key]).relative_to('/workspace')
        if '..' in relative.parts:
            raise ValueError('unsafe container artifact path')
        result[key] = str(config.ROOT / relative)
    result['container_image_id'] = image_id
    result['container_bridge_sha256'] = sha(Path(__file__))
    result = reference_clock(result, out)
    (out / 'host_replay.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def reference_clock(result, out):
    """Apply the approved 10 ns measurement clock to both verified native traces."""
    if result['expected_period_s'] != 1e-9 or result['bounds'] is not None:
        raise ValueError('RedMulE native clock contract differs')
    converted, conversions = dict(result), []
    for field, name in [('waveform', 'power_gls.vcd'), ('rtl_waveform', 'power_rtl.vcd')]:
        target = out / name
        conversions.append(reference_clock_vcd(Path(result[field]), target, 10))
        converted[field] = str(target)
    converted['expected_period_s'] = 1e-8
    receipt = {'schema': 'common-reference-clock-v1', 'native_period_s': 1e-9,
               'expected_period_s': 1e-8, 'conversions': conversions,
               'native_replay': result,
               'claim': 'Fixed reference clock, not timing closure; native scores unchanged'}
    (out / 'power_clock.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return converted
