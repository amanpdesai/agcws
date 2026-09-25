"""Read configuration evidence emitted by the original compiled simulator."""

ENUM_VALUES = {
    'ibex_pkg::BaseIsaRV32IorCHERIoT': 1,
    'ibex_pkg::RV32MFast': 2, 'ibex_pkg::RV32BNone': 0,
    'ibex_pkg::RV32ZcaZcbZcmp': 3, 'ibex_pkg::RegFileFF': 0,
}


def verify_parameters(observed, expected):
    """Reject any missing or different mapped configuration parameter."""
    numeric = {}
    for name, value in expected.items():
        if isinstance(value, int):
            numeric[name] = value
        elif value in ENUM_VALUES:
            numeric[name] = ENUM_VALUES[value]
        elif value.startswith("32'h"):
            numeric[name] = int(value[4:], 16)
        else:
            raise ValueError(f'unsupported parameter expression: {name}={value}')
    differences = {name: {'expected': value, 'observed': observed.get(name)}
                   for name, value in numeric.items() if observed.get(name) != value}
    if differences:
        raise ValueError(f'RTL/synthesis configuration differs: {differences}')
    return numeric


def waveform_parameters(stream, scope):
    stack, identifiers, values = [], {}, {}
    for line in stream:
        fields = line.split()
        if not fields:
            continue
        if fields[0] == '$scope':
            stack.append(fields[2])
        elif fields[0] == '$upscope':
            stack.pop()
        elif fields[0] == '$var' and fields[1] == 'parameter' and '.'.join(stack) == scope:
            identifiers.setdefault(fields[3], []).append(fields[4])
        elif fields[0].startswith('#') and int(fields[0][1:]) > 0:
            break
        elif fields[0].startswith('b') and len(fields) == 2:
            if fields[1] in identifiers:
                if set(fields[0][1:]) - {'0', '1'}:
                    raise ValueError('unknown configuration parameter value')
                for name in identifiers[fields[1]]:
                    values[name] = int(fields[0][1:], 2)
        elif fields[0][0] in '01xzXZ' and fields[0][1:] in identifiers:
            if fields[0][0] not in '01':
                raise ValueError('unknown configuration parameter value')
            for name in identifiers[fields[0][1:]]:
                values[name] = int(fields[0][0])
    if not identifiers or set(values) != {name for names in identifiers.values() for name in names}:
        raise ValueError('incomplete waveform parameter evidence')
    return values
