import time

import machine

from units import Base, Sidings, PairedTurnout

from mcp23017 import MCP23017

i2c1 = machine.I2C(1)


MCPT1 = MCP23017(i2c1, address=0x21)
MCPT2 = MCP23017(i2c1, address=0x24)
MCPB1 = MCP23017(i2c1, address=0x22)

if True:
    sidings = Sidings(
        motor1=MCPT1[0],
        motor2=MCPT1[1],
        motor3=MCPT1[2],
        motor4=MCPT1[3],
        sensor1_straight=MCPT1[14],
        sensor1_diverging=MCPT1[15],
        sensor2_straight=MCPT1[12],
        sensor2_diverging=MCPT1[13],
        sensor3_straight=MCPT1[10],
        sensor3_diverging=MCPT1[11],
        sensor4_straight=MCPT1[9],
        sensor4_diverging=MCPT1[8],
        switch1=MCPB1[15],
        switch2=MCPB1[14],
        switch3=MCPB1[13],
        switch4=MCPB1[12],
        switch5=MCPB1[11],
        led1=MCPB1[0],
        led2=MCPB1[1],
        led3=MCPB1[2],
        led4=MCPB1[3],
        led5=MCPB1[4],
    )

    station_left = PairedTurnout(
        motor=MCPT1[4],
        sensor1_straight=MCPT2[15],
        sensor1_diverging=MCPT2[14],
        sensor2_straight=MCPT2[12],
        sensor2_diverging=MCPT2[13],
        switch_straight=MCPB1[10],
        switch_diverging=MCPB1[9],
        led_straight=MCPB1[5],
        led_diverging=MCPB1[6],
    )

    while True:
        Base.poll_all_switches()
        time.sleep(0.1)
        Base.poll_all_states()
        time.sleep(0.1)
