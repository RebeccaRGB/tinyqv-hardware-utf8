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
    assert await tqv.read_reg(4) == 0xFF

    dut._log.info("Test project behavior")

    # Test register write and read back
    await tqv.write_reg(4, 0x00)
    assert await tqv.read_reg(4) == 0x81

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
    await tqv.write_reg(4, 0xFF)
    assert await tqv.read_reg(4) == 0xFF
    await tqv.write_reg(0, 0x00)
    assert await tqv.read_reg(4) == 0x81
    await tqv.write_reg(0, 0xFF)
    assert await tqv.read_reg(4) == 0xFF
    await tqv.write_reg(4, 0x00)
    assert await tqv.read_reg(4) == 0x81
    await tqv.reset()
    assert await tqv.read_reg(4) == 0xFF

    OUTR = 0x01 # output reset
    ERRS = 0x02 # errors/properties output
    CHKR = 0x04 # range check
    IOBE = 0x08 # big endian I/O
    READ = 0x10 # read/write mode
    CCLK = 0x20 # UTF-32 mode
    UCLK = 0x40 # UTF-16 mode
    BCLK = 0x60 # UTF-8 mode
    INPR = 0x80 # input reset

    UEOF = 0x40 # UTF-16 EOF
    BEOF = 0x80 # UTF-8 EOF

    async def clear_input(b):
        ctl = await tqv.read_reg(4)
        ctl &=~ b
        await tqv.write_reg(0, ctl)
        assert await tqv.read_reg(4) == (ctl | 0x81)

    async def set_input(b):
        ctl = await tqv.read_reg(4)
        ctl |= b
        await tqv.write_reg(0, ctl)
        assert await tqv.read_reg(4) == (ctl | 0x81)

    async def get_output(b):
        ep = await tqv.read_reg(0)
        return (1 if (ep & b) else 0)

    async def write_byte(b, eof):
        await clear_input(READ)
        await tqv.write_reg(1, b)
        assert await get_output(BEOF) == eof

    async def read_byte(b, eof):
        await set_input(READ)
        await tqv.write_reg(1, 0)
        assert await tqv.read_reg(1) == b
        assert await get_output(BEOF) == eof

    async def write_char(b):
        await clear_input(READ)
        await tqv.write_reg(3, b)

    async def read_char(b):
        await set_input(READ)
        await tqv.write_reg(3, 0)
        assert await tqv.read_reg(3) == b

    async def read_reset():
        await clear_input(OUTR)

    async def write_reset():
        await clear_input(INPR)



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

