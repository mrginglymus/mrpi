import time

import machine

from units import Base, Sidings, PairedTurnout, Turnout, Crossover

from mcp23017 import MCP23017

i2c1 = machine.I2C(1)


MCPT1 = MCP23017(i2c1, address=0x21)
MCPT2 = MCP23017(i2c1, address=0x24)
MCPT3 = MCP23017(i2c1, address=0x20)
MCPB1 = MCP23017(i2c1, address=0x22)
MCPB2 = MCP23017(i2c1, address=0x23)

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

    station_right = PairedTurnout(
        motor=MCPT1[5],
        sensor1_straight=MCPT2[10],
        sensor1_diverging=MCPT2[11],
        sensor2_straight=MCPT2[9],
        sensor2_diverging=MCPT2[12],
        switch_straight=MCPB1[8],
        switch_diverging=MCPB2[15],
        led_straight=MCPB1[7],
        led_diverging=MCPB2[0],
    )

    program = Turnout(
        motor=MCPT1[6],
        sensor_straight=MCPT2[1],
        sensor_diverging=MCPT2[0],
        switch_straight=MCPB2[14],
        switch_diverging=MCPB2[13],
        led_straight=MCPB2[1],
        led_diverging=MCPB2[2],
    )

    sidings_entrance = Turnout(
        motor=MCPT1[7],
        sensor_straight=MCPT2[3],
        sensor_diverging=MCPT2[2],
        switch_straight=MCPB2[12],
        switch_diverging=MCPB2[11],
        led_straight=MCPB2[3],
        led_diverging=MCPB2[4],
    )

    slip = Crossover(
        motor1=MCPT3[0],
        motor2=MCPT3[1],
        sensor1_straight=MCPT2[4],
        sensor1_diverging=MCPT2[5],
        sensor2_straight=MCPT2[6],
        sensor2_diverging=MCPT2[7],
        sensor3_straight=MCPT3[15],
        sensor3_diverging=MCPT3[14],
        sensor4_straight=MCPT3[13],
        sensor4_diverging=MCPT3[12],
        switch_straight=MCPB2[5],
        switch_diverging=MCPB2[6],
        switch_partial=MCPB2[7],
        led_straight=MCPB2[10],
        led_diverging=MCPB2[9],
        led_partial=MCPB2[8],
    )

    while False:
        Base.poll_all_switches()
        time.sleep(0.1)
        Base.poll_all_states()
        time.sleep(0.1)
