import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, ReadWrite, NextTimeStep
from cocotb.clock import Clock
from cocotb.utils import get_sim_time

@cocotb.test()
async def flipflop_test(dut):

    dut._log.info("Starting flip-flop test, showing initial values")
    dut._log.info("clk=%s, d=%s, q=%s (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())
    
    dut.d.value = 1
    dut._log.info("Assigned 1 to d, but value will only be assigned after an await call.")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await RisingEdge(dut.clk)
    dut._log.info("After first rising edge d is updated, but q is not")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await RisingEdge(dut.clk)
    dut._log.info("After second rising edge q is updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    dut.d.value = 1 - dut.d.value
    dut._log.info("Assigned %s to d, but value will only be assigned after an await call.", (1 - dut.d.value))
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await RisingEdge(dut.clk)
    dut._log.info("After first rising edge d is updated, but q is not")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await ReadOnly()
    dut._log.info("After ReadOnly q is updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    await RisingEdge(dut.clk)

    dut.d.value = 1 - dut.d.value
    dut._log.info("Assigned %s to d, but value will only be assigned after an await call.", (1 - dut.d.value))
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await RisingEdge(dut.clk)
    dut._log.info("After first rising edge d is updated, but q is not")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await NextTimeStep()
    dut._log.info("After NextTimeStep q is updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    dut.d.value = 1 - dut.d.value
    dut._log.info("Assigned %s to d, but value will only be assigned after an await call.", (1 - dut.d.value))
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await RisingEdge(dut.clk)
    dut._log.info("After first rising edge d is updated, but q is not")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await ReadWrite()
    dut._log.info("After ReadWrite q is updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    dut.d.value = 1 - dut.d.value
    dut._log.info("Assigned %s to d, but value will only be assigned after an await call.", (1 - dut.d.value))
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await ReadOnly()
    dut._log.info("After ReadOnly d is updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    await RisingEdge(dut.clk)
    await NextTimeStep()

    dut.d.value = 1 - dut.d.value
    dut._log.info("Assigned %s to d, but value will only be assigned after an await call.", (1 - dut.d.value))
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await ReadWrite()
    dut._log.info("After ReadWrite d is not updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()

    await RisingEdge(dut.clk)
    await NextTimeStep()

    dut.d.value = 1 - dut.d.value
    dut._log.info("Assigned %s to d, but value will only be assigned after an await call.", (1 - dut.d.value))
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    await NextTimeStep()
    dut._log.info("After NextTimeStep d is not updated")
    dut._log.info("clk=%s, d=%s, q=%s, (%d ns)", dut.clk.value, dut.d.value, dut.q.value, get_sim_time("ns"))
    print()


    # await ReadOnly()
    # dut._log.info("ReadWrite after ReadOnly crashes the simulation.")
    # await ReadWrite()