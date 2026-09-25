"""Translate temporal schedules into fixed-data AES-128 encryption and idle commands."""
from agcws.designs.aes.transactions import AESTransactionAdapter
from agcws.designs.temporal import TemporalScheduleAdapter
from agcws.designs.workloads.schedule import expand_schedule


def lower_schedule(schedule, contract):
    operations = [{'op': 'configure', 'key_len': 128}]
    for node in expand_schedule(schedule, contract):
        operations.append({'op': 'encrypt', 'blocks': node['units']} if node['op'] == 'work'
                          else {'op': 'idle', 'cycles': node['cycles']})
    return {'data_pattern': 1, 'operations': operations}


class AESTemporalAdapter(TemporalScheduleAdapter):
    name = AESTransactionAdapter.name
    regions = AESTransactionAdapter.regions
    activity_region_prefixes = AESTransactionAdapter.activity_region_prefixes
    design_summary = ('AES-128 encryption with fixed key/data. A work unit encrypts one block; '
                      'wait cycles pace the core. Sequence order controls temporal activity.')

    def elaborate(self, workload):
        return lower_schedule(workload, self.contract)
