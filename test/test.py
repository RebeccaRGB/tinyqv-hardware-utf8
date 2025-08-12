# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from tqv import TinyQV

# When submitting your design, change this to 16 + the peripheral number
# in peripherals.v.  e.g. if your design is i_user_simple00, set this to 16.
# The peripheral number is not used by the test harness.
PERIPHERAL_NUM = 16

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Interact with your design's registers through this TinyQV class.
    # This will allow the same test to be run when your design is integrated
    # with TinyQV - the implementation of this class will be replaces with a
    # different version that uses Risc-V instructions instead of the SPI 
    # interface to read and write the registers.
    tqv = TinyQV(dut, PERIPHERAL_NUM)

    # Reset, always start the test by resetting TinyQV
    await tqv.reset()
    assert await tqv.read_reg(0) == 0
    assert await tqv.read_reg(1) == 0
    assert await tqv.read_reg(2) == 0
    assert await tqv.read_reg(3) == 0
    assert await tqv.read_reg(4) == 0
    assert await tqv.read_reg(5) == 0
    assert await tqv.read_reg(6) == 0
    assert await tqv.read_reg(7) == 0
    assert await tqv.read_reg(8) == 0
    assert await tqv.read_reg(9) == 0
    assert await tqv.read_reg(10) == 0
    assert await tqv.read_reg(11) == 0
    assert await tqv.read_reg(12) == 0
    assert await tqv.read_reg(13) == 0
    assert await tqv.read_reg(14) == 0
    assert await tqv.read_reg(15) == 0

    dut._log.info("Test project behavior")

    # Test register write and read back
    await tqv.write_reg(3, 0x41)
    assert await tqv.read_reg(0) == 1
    assert await tqv.read_reg(1) == 1
    assert await tqv.read_reg(2) == 2
    assert await tqv.read_reg(3) == 1
    assert await tqv.read_reg(4) == 0
    assert await tqv.read_reg(5) == 0
    assert await tqv.read_reg(6) == 0
    assert await tqv.read_reg(7) == 0
    assert await tqv.read_reg(8) == 0
    assert await tqv.read_reg(9) == 0
    assert await tqv.read_reg(10) == 0
    assert await tqv.read_reg(11) == 0x41
    assert await tqv.read_reg(12) == 0
    assert await tqv.read_reg(13) == 0
    assert await tqv.read_reg(14) == 0
    assert await tqv.read_reg(15) == 0x41

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
    await tqv.write_reg(0, 0xFF)
    assert await tqv.read_reg(0) == 0
    assert await tqv.read_reg(1) == 0
    assert await tqv.read_reg(2) == 0
    assert await tqv.read_reg(3) == 0
    assert await tqv.read_reg(4) == 0
    assert await tqv.read_reg(5) == 0
    assert await tqv.read_reg(6) == 0
    assert await tqv.read_reg(7) == 0
    assert await tqv.read_reg(8) == 0
    assert await tqv.read_reg(9) == 0
    assert await tqv.read_reg(10) == 0
    assert await tqv.read_reg(11) == 0
    assert await tqv.read_reg(12) == 0
    assert await tqv.read_reg(13) == 0
    assert await tqv.read_reg(14) == 0
    assert await tqv.read_reg(15) == 0

    global ctl
    ctl = 0xFF

    ERRS = 0x02 # errors/properties output
    CHKR = 0x04 # range check
    IOBE = 0x08 # big endian I/O

    async def clear_input(b):
        global ctl
        ctl &=~ b
        await tqv.write_reg(4, ctl)

    async def set_input(b):
        global ctl
        ctl |= b
        await tqv.write_reg(4, ctl)

    async def write_byte(b, eof):
        await tqv.write_reg(3, b)
        u8len = await tqv.read_reg(3)
        assert (1 if ((u8len & 15) >= 6) else 0) == eof

    async def read_byte(b, eof):
        await tqv.write_reg(7, 0)
        assert await tqv.read_reg(7) == b
        u8len = await tqv.read_reg(3)
        assert (1 if (u8len & 128) else 0) == eof

    async def write_char(b):
        await tqv.write_reg(1, b)

    async def read_char(b):
        await tqv.write_reg(5, 0)
        assert await tqv.read_reg(5) == b

    async def read_reset():
        global ctl
        await tqv.write_reg(4, ctl)

    async def write_reset():
        global ctl
        await tqv.write_reg(0, ctl)


    # register I/O

    # write to byte buffer
    await write_byte(0xFD, 0)
    await write_byte(0xBE, 0)
    await write_byte(0xAC, 0)
    await write_byte(0x97, 0)
    await write_byte(0x86, 0)
    await write_byte(0xB5, 1)
    await write_byte(0xA4, 1)

    # read from byte buffer
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 0)
    await read_byte(0x97, 0)
    await read_byte(0x86, 0)
    await read_byte(0xB5, 1)
    await read_byte(0, 1)

    # read from byte buffer again
    await read_reset()
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 0)
    await read_byte(0x97, 0)
    await read_byte(0x86, 0)
    await read_byte(0xB5, 1)
    await read_byte(0, 1)

    await write_reset()

    # write to character buffer, big endian
    await write_char(11)
    await write_char(22)
    await write_char(33)
    await write_char(44)
    await write_char(55)

    # read from character buffer, big endian
    await read_char(11)
    await read_char(22)
    await read_char(33)
    await read_char(44)
    await read_char(0)

    # read from character buffer again
    await read_reset()
    await read_char(11)
    await read_char(22)
    await read_char(33)
    await read_char(44)
    await read_char(0)

    await clear_input(IOBE)
    await write_reset()

    # write to character buffer, little endian
    await write_char(11)
    await write_char(22)
    await write_char(33)
    await write_char(44)
    await write_char(55)

    # read from character buffer, little endian
    await read_char(11)
    await read_char(22)
    await read_char(33)
    await read_char(44)
    await read_char(0)

    # read from character buffer again
    await read_reset()
    await read_char(11)
    await read_char(22)
    await read_char(33)
    await read_char(44)
    await read_char(0)

    await set_input(IOBE)
    await write_reset()

    # write to byte buffer
    await write_byte(0xFD, 0)
    await write_byte(0xBE, 0)
    await write_byte(0xAC, 0)

    # read from byte buffer
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 1)
    await read_byte(0, 1)

    # read from byte buffer again
    await read_reset()
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 1)
    await read_byte(0, 1)

    await write_reset()

    # write to character buffer, big endian
    await write_char(111)
    await write_char(222)

    # read from character buffer, big endian
    await read_char(0)
    await read_char(0)
    await read_char(111)
    await read_char(222)
    await read_char(0)

    # read from character buffer again
    await read_reset()
    await read_char(0)
    await read_char(0)
    await read_char(111)
    await read_char(222)
    await read_char(0)

    await clear_input(IOBE)
    await write_reset()

    # write to character buffer, little endian
    await write_char(111)
    await write_char(222)

    # read from character buffer, little endian
    await read_char(111)
    await read_char(222)
    await read_char(0)
    await read_char(0)
    await read_char(0)

    # read from character buffer again
    await read_reset()
    await read_char(111)
    await read_char(222)
    await read_char(0)
    await read_char(0)
    await read_char(0)

    await set_input(IOBE)
    await write_reset()

