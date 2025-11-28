import time
from collections.abc import Callable

import machine

from mcp23017 import VirtualPin, MCP23017


class Motor:
    def __init__(
        self,
        pin: VirtualPin,
        *,
        on: Callable[[], bool],
        off: Callable[[], bool],
        default: bool = False
    ):
        self._pin = pin
        self.on = on
        self.off = off
        self._pin.output(default)

    def poll(self):
        if self.on():
            self._pin.output(True)
        elif self.off():
            self._pin.output(False)


class Switch:
    def __init__(
        self, switch: VirtualPin, led: VirtualPin, *, value: Callable[[], bool]
    ):
        self.switch = switch
        self.switch.input(True)
        self.led = led
        self.get_value = value
        self.poll()

    @property
    def value(self):
        return self.switch.value()

    def poll(self):
        self.led.output(self.get_value())


class LED:
    def __init__(self, pin: VirtualPin, *, default: bool):
        self._pin = pin
        self._pin.output(default)

    def output(self, value: bool):
        self._pin.output(value)


class DebouncedPin:
    def __init__(self, pin: VirtualPin, *, threshold: float = 0.2):
        self._pin = pin
        self._threshold = threshold
        self._last_time = 0
        self._pin.input(True)
        self._value = self._pin.value()

    @property
    def value(self):
        self.poll()
        return self._value

    def poll(self):
        if self._pin.value:
            if self._last_time == 0:
                self._last_time = time.time()
            elif (time.time() - self._last_time) > self._threshold:
                self._value = True
        else:
            self._value = False


class Sensor:
    def __init__(self, *, straight: VirtualPin, diverging: VirtualPin):
        self._straight = DebouncedPin(straight)
        self._diverging = DebouncedPin(diverging)

    @property
    def straight(self):
        return self._straight.value

    @property
    def diverging(self):
        return self._diverging.value


class Base:
    def __init__(self, *, motors: list[Motor], switches: list[Switch]):
        self.motors = motors
        self.switches = switches

    def poll_input(self):
        for motor in self.motors:
            motor.poll()

    def poll_output(self):
        for switch in self.switches:
            switch.poll()


class Turnout(Base):
    def __init__(
        self,
        *,
        motor: VirtualPin,
        switch_straight: VirtualPin,
        switch_diverging: VirtualPin,
        sensor_straight: VirtualPin,
        sensor_diverging: VirtualPin,
        led_straight: VirtualPin,
        led_diverging: VirtualPin
    ):
        sensor = Sensor(straight=sensor_straight, diverging=sensor_diverging)

        switch_straight = Switch(
            switch_straight, led_straight, value=lambda: sensor.straight
        )
        switch_diverging = Switch(
            switch_diverging, led_diverging, value=lambda: sensor.diverging
        )

        motor = Motor(
            motor,
            default=sensor.diverging,
            on=lambda: switch_diverging.value,
            off=lambda: switch_straight.value,
        )
        super().__init__(motors=[motor], switches=[switch_straight, switch_diverging])


class Crossover(Base):
    def __init__(
        self,
        *,
        motor: VirtualPin,
        switch_straight: VirtualPin,
        switch_diverging: VirtualPin,
        sensor1_straight: VirtualPin,
        sensor1_diverging: VirtualPin,
        sensor2_straight: VirtualPin,
        sensor2_diverging: VirtualPin,
        led_straight: VirtualPin,
        led_diverging: VirtualPin
    ):
        sensor1 = Sensor(straight=sensor1_straight, diverging=sensor1_diverging)
        sensor2 = Sensor(straight=sensor2_straight, diverging=sensor2_diverging)

        switch_straight = Switch(
            switch_straight,
            led_straight,
            value=lambda: sensor1.straight and sensor2.straight,
        )
        switch_diverging = Switch(
            switch_diverging,
            led_diverging,
            value=lambda: sensor1.diverging and sensor2.diverging,
        )

        motor = Motor(
            motor,
            default=False,
            on=lambda: switch_diverging.value,
            off=lambda: switch_straight.value,
        )
        super().__init__(motors=[motor], switches=[switch_straight, switch_diverging])


class SingleSlip(Base):
    def __init__(
        self,
        *,
        motor1: VirtualPin,
        motor2: VirtualPin,
        switch_straight: VirtualPin,
        switch_diverging: VirtualPin,
        switch_partial: VirtualPin,
        led_straight: VirtualPin,
        led_diverging: VirtualPin,
        led_partial: VirtualPin,
        sensor1_straight: VirtualPin,
        sensor1_diverging: VirtualPin,
        sensor2_straight: VirtualPin,
        sensor2_diverging: VirtualPin,
        sensor3_straight: VirtualPin,
        sensor3_diverging: VirtualPin
    ):
        sensor1 = Sensor(straight=sensor1_straight, diverging=sensor1_diverging)
        sensor2 = Sensor(straight=sensor2_straight, diverging=sensor2_diverging)
        sensor3 = Sensor(straight=sensor3_straight, diverging=sensor3_diverging)
        switch_straight = Switch(
            switch_straight,
            led_straight,
            value=lambda: sensor1.straight and sensor2.straight and sensor3.straight,
        )
        switch_diverging = Switch(
            switch_diverging,
            led_diverging,
            value=lambda: sensor1.diverging and sensor2.diverging and sensor3.diverging,
        )
        switch_partial = Switch(
            switch_partial,
            led_partial,
            value=lambda: sensor1.straight and sensor2.diverging,
        )

        # todo: this logic
        motor1 = Motor(
            motor1,
            default=False,
            on=lambda: switch_straight.value or switch_partial.value,
            off=lambda: switch_diverging.value,
        )
        motor2 = Motor(
            motor2,
            default=False,
            on=lambda: switch_straight.value or switch_partial.value,
            off=lambda: switch_diverging.value,
        )
        super().__init__(
            motors=[motor1, motor2],
            switches=[switch_straight, switch_diverging, switch_partial],
        )


i2c = machine.I2C(1)
MCP = MCP23017(i2c)

sidings = Turnout(
    motor=MCP.porta[0],
    switch_straight=MCP.portb[0],
    switch_diverging=MCP.portb[1],
    sensor_straight=MCP.portb[2],
    sensor_diverging=MCP.portb[3],
    led_straight=MCP.porta[1],
    led_diverging=MCP.porta[2],
)

while True:
    sidings.poll_input()
    time.sleep(0.1)
    sidings.poll_output()
    time.sleep(0.1)
