import time

import machine

from units import Turnout

from mcp23017 import MCP23017

i2c1 = machine.I2C(1)

MCP20 = MCP23017(i2c1, address=0x20)

if True:
    sidings = Turnout(
        motor=MCP20[0],
        sensor_straight=MCP20[13],
        sensor_diverging=MCP20[12],
        switch_straight=MCP20[15],
        led_straight=MCP20[1],
        switch_diverging=MCP20[14],
        led_diverging=MCP20[2],
    )

    while True:
        sidings.poll_switches()
        time.sleep(0.1)
        sidings.poll_state()
        time.sleep(0.1)
