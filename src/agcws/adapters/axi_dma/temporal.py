"""Lower structural work groups to independent reference-checked DMA copies."""
from agcws.adapters.axi_dma.pipelined import PipelinedDmaAdapter
from agcws.adapters.temporal import TemporalScheduleAdapter
from agcws.nodes.validation import validate_static
from agcws.workloads.schedule import expand_schedule


def lower_schedule(schedule, contract):
    if not 64 <= contract.work_units <= 128:
        raise ValueError('DMA temporal contract requires 64..128 units of 64 bytes')
    transfers, gap = [], 0
    for node in expand_schedule(schedule, contract):
        if node['op'] == 'wait':
            gap += node['cycles']
            continue
        remaining = node['units']
        while remaining:
            depth = min(8, remaining)
            for index in range(depth):
                transfers.append({'src': index * 4096, 'dst': (index + 8) * 4096,
                                  'length': 64, 'outstanding': depth,
                                  'gap_cycles': gap if index == 0 else 0})
            gap = 0
            remaining -= depth
    workload = {'transfers': transfers,
                'backpressure': {'period': 1, 'read_pause': 0, 'write_pause': 0}}
    validity = validate_static(PipelinedDmaAdapter(), workload)
    if not validity.valid:
        raise ValueError(validity.reason)
    return {'workload': workload, 'trailing_idle_cycles': gap}


class DmaTemporalAdapter(TemporalScheduleAdapter):
    name = 'verilog_axi_dma'
    work_quantum = 64
    design_summary = ('DMA copies memory through read and write channels. Each work unit is a '
                      '64-byte copy. Consecutive units within a work operation issue in groups '
                      'of up to eight concurrent transfers; each group completes before the next. '
                      'Wait cycles delay read issuance; splitting work can reduce concurrency. '
                      'All transfers and declared waits must finish within the fixed observation horizon.')

    def __init__(self, contract):
        super().__init__(contract)
        if not 64 <= contract.work_units <= 128:
            raise ValueError('DMA temporal contract requires 64..128 units of 64 bytes')

    def elaborate(self, workload):
        return lower_schedule(workload, self.contract)
