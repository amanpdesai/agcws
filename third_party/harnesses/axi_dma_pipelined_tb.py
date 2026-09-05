"""Reference-checked concurrent descriptor groups with observed handshakes."""
import itertools
import json
import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge
from cocotbext.axi import AxiBus, AxiRam, AxiStreamFrame
from axi_dma_coupled_tb import (DescBus, DescSource, DescTransaction, StatusBus, StatusSink,
                                 cocotbext_read_sink, cocotbext_write_source)
from agcws.adapters.axi_dma.pipelined import PipelinedDmaAdapter, groups
from agcws.nodes.validation import validate_static


@cocotb.test()
async def run_workload(dut):
    with open(os.environ['AGCWS_DMA_WORKLOAD']) as source:
        workload = json.load(source)
    validity = validate_static(PipelinedDmaAdapter(), workload)
    assert validity.valid, validity.reason
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    dut.read_enable.value = 0
    dut.write_enable.value = 0
    dut.write_abort.value = 0
    read_desc = DescSource(DescBus.from_prefix(dut, 's_axis_read_desc'), dut.clk, dut.rst)
    write_desc = DescSource(DescBus.from_prefix(dut, 's_axis_write_desc'), dut.clk, dut.rst)
    read_status = StatusSink(StatusBus.from_prefix(dut, 'm_axis_read_desc_status'), dut.clk, dut.rst)
    write_status = StatusSink(StatusBus.from_prefix(dut, 'm_axis_write_desc_status'), dut.clk, dut.rst)
    read_data, write_data = cocotbext_read_sink(dut), cocotbext_write_source(dut)
    ram = AxiRam(AxiBus.from_prefix(dut, 'm_axi'), dut.clk, dut.rst, size=65536)
    pause = workload.get('backpressure', {'period': 1, 'read_pause': 0, 'write_pause': 0})
    read_data.set_pause_generator(itertools.cycle([True] * pause['read_pause'] +
                                                [False] * (pause['period'] - pause['read_pause'])))
    write_data.set_pause_generator(itertools.cycle([True] * pause['write_pause'] +
                                                 [False] * (pause['period'] - pause['write_pause'])))
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut.read_enable.value = 1
    dut.write_enable.value = 1
    observed = {'read_descriptors': 0, 'write_completions': 0, 'max_inflight': 0}

    async def monitor():
        while True:
            await FallingEdge(dut.clk)
            accepted = int(dut.s_axis_read_desc_valid.value) and int(dut.s_axis_read_desc_ready.value)
            done = int(dut.m_axis_write_desc_status_valid.value)
            await RisingEdge(dut.clk)
            observed['read_descriptors'] += int(accepted)
            observed['write_completions'] += done
            observed['max_inflight'] = max(observed['max_inflight'],
                                           observed['read_descriptors'] - observed['write_completions'])
    watcher = cocotb.start_soon(monitor())
    tag = 0
    for group in groups(workload['transfers']):
        records = []
        for transfer in group:
            tag += 1
            data = bytes((transfer['src'] + i) % 256 for i in range(transfer['length']))
            ram.write(transfer['src'], data)
            ram.write(transfer['dst'], bytes(transfer['length']))
            records.append((tag, transfer, data))

        async def issue_reads():
            for ident, transfer, _ in records:
                for _ in range(transfer.get('gap_cycles', 0)):
                    await RisingEdge(dut.clk)
                await read_desc.send(DescTransaction(addr=transfer['src'], len=transfer['length'], tag=ident))

        async def issue_writes():
            for ident, transfer, _ in records:
                await write_desc.send(DescTransaction(addr=transfer['dst'], len=transfer['length'], tag=ident))

        async def bridge():
            for ident, _, data in records:
                frame = await read_data.recv()
                assert bytes(frame.tdata) == data
                await write_data.send(AxiStreamFrame(frame.tdata, tid=ident))

        tasks = [cocotb.start_soon(fn()) for fn in [issue_reads, issue_writes, bridge]]
        for ident, transfer, data in records:
            read, write = await read_status.recv(), await write_status.recv()
            assert int(read.error) == int(write.error) == 0
            assert int(read.tag) == int(write.tag) == ident
            assert ram.read(transfer['dst'], transfer['length']) == data
        for task in tasks:
            await task
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    watcher.cancel()
    assert observed['read_descriptors'] == observed['write_completions'] == len(workload['transfers'])
    with open('observed.json', 'w') as result:
        json.dump(observed, result)
    dut._log.info('AGCWS_AXI_DMA_PIPELINED_OK transfers=%d max_inflight=%d', tag, observed['max_inflight'])
