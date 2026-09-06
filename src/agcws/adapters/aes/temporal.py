"""Fixed AES-128 encryption lowering for the structural temporal pilot."""
from agcws.workloads.schedule import expand_schedule


def lower_schedule(schedule, contract):
    operations = [{'op': 'configure', 'key_len': 128}]
    for node in expand_schedule(schedule, contract):
        operations.append({'op': 'encrypt', 'blocks': node['units']} if node['op'] == 'work'
                          else {'op': 'idle', 'cycles': node['cycles']})
    return {'data_pattern': 1, 'operations': operations}
