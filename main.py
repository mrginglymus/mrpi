import time

import machine

# from collections.abc import Callable

from mcp23017 import VirtualPin, MCP23017

PULL_HIGH = True
ON = False
OFF = True

class Motor:
    def __init__(
        self,
        pin: VirtualPin,
        *,
        straight: Callable[[], bool],
        diverging: Callable[[], bool],
        default: bool
    ):
        self._pin = pin
        self.straight = straight
        self.diverging = diverging
        self._pin.output(default)

    def poll(self):
        if self.straight():
            self._pin.output(ON)
        elif self.diverging():
            self._pin.output(OFF)


class Switch:
    def __init__(
        self, switch: VirtualPin, led: VirtualPin, *, value: Callable[[], bool]
    ):
        self.switch = switch
        self.switch.input(PULL_HIGH)
        self.led = led
        self.get_value = value
        self.poll()

    @property
    def pressed(self):
        return not self.switch.value()

    def poll(self):
        self.led.output(not self.get_value())


class DebouncedPin:
    def __init__(self, pin: VirtualPin, *, threshold: float = 0.2):
        self._pin = pin
        self._threshold = threshold
        self._last_time = 0
        self._pin.input(PULL_HIGH)
        self._value = self._pin.value()

    def __bool__(self):
        self.poll()
        return self._value

    def poll(self):
        if self._pin.value() is OFF:
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
        return bool(self._straight)
    
    @property
    def diverging(self):
        return bool(self._diverging)


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
            default=sensor.straight,
            straight=lambda: switch_straight.pressed,
            diverging=lambda: switch_diverging.pressed,
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
            default=OFF,
            straight=lambda: bool(switch_straight),
            diverging=lambda: bool(switch_diverging),
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
            default=OFF,
            straight=lambda: switch_straight.pressed or switch_partial.pressed,
            diverging=lambda: switch_diverging.pressed,
        )
        motor2 = Motor(
            motor2,
            default=OFF,
            straight=lambda: switch_straight.pressed or switch_partial.pressed,
            diverging=lambda: switch_diverging.pressed,
        )
        super().__init__(
            motors=[motor1, motor2],
            switches=[switch_straight, switch_diverging, switch_partial],
        )


i2c = machine.I2C(1)

MCP = MCP23017(i2c)

if True:
    sidings = Turnout(
        motor=MCP[0],
        switch_straight=MCP[15],
        switch_diverging=MCP[14],
        sensor_straight=MCP[13],
        sensor_diverging=MCP[12],
        led_straight=MCP[1],
        led_diverging=MCP[2],
    )

    while True:
        sidings.poll_input()
        time.sleep(0.1)
        sidings.poll_output()
        time.sleep(0.1)
