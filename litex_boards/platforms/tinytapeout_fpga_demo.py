#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Tim Ansell <me@mith.ro>
# SPDX-License-Identifier: BSD-2-Clause

# TinyTapeout FPGA Demo Board:
# - TinyTapeout site: https://tinytapeout.com
# - FPGA breakout guide: https://tinytapeout.com/guides/fpga-breakout/
# - Demo PCB design: https://github.com/TinyTapeout/tt-demo-pcb
#
# The board consists of two PCBs:
#   - TinyTapeout Demo PCB (bottom): RP2040 controller, USB-C, 7-segment
#     display, DIP switches, PMOD headers
#   - FPGA Breakout Board (top): Lattice iCE40UP5K (SG48) + SPI flash,
#     plugs into the demo PCB's chip socket
#
# The RP2040 provides a 50 MHz clock to the FPGA and can act as a
# USB-to-UART bridge for serial communication.
#
# Programming: The RP2040 programs the iCE40 over SPI using the fabricfox
# MicroPython module via mpremote. IceStormProgrammer (iceprog) is provided
# as a fallback for direct SPI flash programming with an external adapter.

from litex.build.generic_platform import *
from litex.build.lattice import LatticeiCE40Platform
from litex.build.lattice.programmer import IceStormProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("20"), IOStandard("LVCMOS33")),
    ("rst_n", 0, Pins("37"), IOStandard("LVCMOS33")),

    # Leds
    ("rgb_led", 0,
        Subsignal("r", Pins("39")),
        Subsignal("g", Pins("40")),
        Subsignal("b", Pins("41")),
        IOStandard("LVCMOS33"),
    ),

    # Serial
    ("serial", 0,
        Subsignal("rx", Pins("21")),   # ui_in[3]
        Subsignal("tx", Pins("45")),   # uo_out[4]
        IOStandard("LVCMOS33"),
    ),

    # TinyTapeout I/O
    ("ui_in",  0, Pins("13 19 18 21 23 25 26 27"), IOStandard("LVCMOS33")),
    ("uo_out", 0, Pins("38 42 43 44 45 46 47 48"), IOStandard("LVCMOS33")),
    ("uio",    0, Pins("2 4 3 6 9 10 11 12"),      IOStandard("LVCMOS33")),

    # SPIFlash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("17"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("14"), IOStandard("LVCMOS33")),
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("16"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("15"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("14 17"), IOStandard("LVCMOS33")),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("tt_input",  "13 19 18 21 23 25 26 27"),   # ui_in[0:7]
    ("tt_output", "38 42 43 44 45 46 47 48"),   # uo_out[0:7]
    ("tt_bidir",  "2 4 3 6 9 10 11 12"),        # uio[0:7]
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeiCE40Platform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="icestorm"):
        LatticeiCE40Platform.__init__(self, "ice40-up5k-sg48", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return IceStormProgrammer()

    def do_finalize(self, fragment):
        LatticeiCE40Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
