"""Parse reported power components without confusing total and dynamic power."""
import math
import re


def parse_report(report):
    total = re.search(r'^Total\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', report, re.MULTILINE)
    annotated = re.search(r'^vcd\s+(\d+)', report, re.MULTILINE)
    missing = re.search(r'^unannotated\s+(\d+)', report, re.MULTILINE)
    if not (total and annotated and missing):
        raise ValueError('missing power or annotation report')
    internal, switching, leakage, power = map(float, total.groups())
    if any(not math.isfinite(v) or v < 0 for v in (internal, switching, leakage, power)):
        raise ValueError('invalid power report')
    if int(annotated[1]) == 0 or internal + switching <= 0:
        raise ValueError('no annotated dynamic power for active-work validation')
    if not math.isclose(internal + switching + leakage, power, rel_tol=1e-6, abs_tol=1e-12):
        raise ValueError('inconsistent power components')
    return {'internal_power_w': internal, 'switching_power_w': switching,
            'dynamic_power_w': internal + switching, 'leakage_power_w': leakage,
            'total_power_w': power, 'annotated_pins': int(annotated[1]),
            'unannotated_pins': int(missing[1])}
