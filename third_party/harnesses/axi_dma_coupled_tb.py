"""Workload-driven cocotb test for the pinned verilog-axi axi_dma top level."""
from __future__ import annotations

import json
import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.axi import AxiBus, AxiRam, AxiStreamBus, AxiStreamFrame
from cocotbext.axi.stream import define_stream


DescBus, DescTransaction, DescSource, _DescSink, _DescMonitor = define_stream(
    "Desc", signals=["addr", "len", "tag", "valid", "ready"],
    optional_signals=["id", "dest", "user"])
StatusBus, _StatusTransaction, _StatusSource, StatusSink, _StatusMonitor = define_stream(
    "Status", signals=["tag", "error", "valid"], optional_signals=["len", "id", "dest", "user"])


@cocotb.test()
async def run_workload(dut):
    with open(os.environ["AGCWS_DMA_WORKLOAD"]) as stream:
        transfers = json.load(stream)["transfers"]
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.read_enable.value = 0
    dut.write_enable.value = 0
    dut.write_abort.value = 0

    read_desc = DescSource(DescBus.from_prefix(dut, "s_axis_read_desc"), dut.clk, dut.rst)
    write_desc = DescSource(DescBus.from_prefix(dut, "s_axis_write_desc"), dut.clk, dut.rst)
    read_status = StatusSink(
        StatusBus.from_prefix(dut, "m_axis_read_desc_status"), dut.clk, dut.rst)
    write_status = StatusSink(
        StatusBus.from_prefix(dut, "m_axis_write_desc_status"), dut.clk, dut.rst)
    read_data = cocotbext_read_sink(dut)
    write_data = cocotbext_write_source(dut)
    ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut.read_enable.value = 1
    dut.write_enable.value = 1

    for tag, transfer in enumerate(transfers, start=1):
        length = int(transfer["length"])
        source = bytes((int(transfer["src"]) + i) % 256 for i in range(length))
        ram.write(int(transfer["src"]), source)
        ram.write(int(transfer["dst"]), b"\x00" * length)
        await read_desc.send(DescTransaction(addr=int(transfer["src"]), len=length, tag=tag))
        await write_desc.send(DescTransaction(addr=int(transfer["dst"]), len=length, tag=tag))
        frame = await read_data.recv()
        await write_data.send(AxiStreamFrame(frame.tdata, tid=tag))
        read_result = await read_status.recv()
        write_result = await write_status.recv()
        assert int(read_result.error) == 0
        assert int(write_result.error) == 0
        assert ram.read(int(transfer["dst"]), length) == source

    dut.read_enable.value = 0
    dut.write_enable.value = 0
    dut._log.info("AGCWS_AXI_DMA_COUPLED_OK transfers=%d", len(transfers))


def cocotbext_read_sink(dut):
    from cocotbext.axi import AxiStreamSink
    return AxiStreamSink(AxiStreamBus.from_prefix(dut, "m_axis_read_data"), dut.clk, dut.rst)


def cocotbext_write_source(dut):
    from cocotbext.axi import AxiStreamSource
    return AxiStreamSource(AxiStreamBus.from_prefix(dut, "s_axis_write_data"), dut.clk, dut.rst)
