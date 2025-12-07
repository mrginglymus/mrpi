import time

import machine

from units import Base, Sidings, PairedTurnout

from mcp23017 import MCP23017

i2c1 = machine.I2C(1)


MCP20 = MCP23017(i2c1, address=0x20)
MCP21 = MCP23017(i2c1, address=0x21)
MCP22 = MCP23017(i2c1, address=0x22)

if True:
    sidings = Sidings(
        motor1=MCP21[0],
        motor2=MCP21[1],
        motor3=MCP21[2],
        motor4=MCP21[3],
        sensor1_straight=MCP21[14],
        sensor1_diverging=MCP21[15],
        sensor2_straight=MCP21[12],
        sensor2_diverging=MCP21[13],
        sensor3_straight=MCP21[10],
        sensor3_diverging=MCP21[11],
        sensor4_straight=MCP21[9],
        sensor4_diverging=MCP21[8],
        switch1=MCP22[15],
        switch2=MCP22[14],
        switch3=MCP22[13],
        switch4=MCP22[12],
        switch5=MCP22[11],
        led1=MCP22[0],
        led2=MCP22[1],
        led3=MCP22[2],
        led4=MCP22[3],
        led5=MCP22[4],
    )
    
    station_left = PairedTurnout(
        motor=MCP21[4],
        sensor1_straight=MCP20[15],
        sensor1_diverging=MCP20[14],
        sensor2_straight=MCP20[12],
        sensor2_diverging=MCP20[13],
        switch_straight=MCP22[10],
        switch_diverging=MCP22[9],
        led_straight=MCP22[5],
        led_diverging=MCP22[6]
    )

    while True:
        Base.poll_all_switches()
        time.sleep(0.1)
        Base.poll_all_states()
        time.sleep(0.1)
