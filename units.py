import time

try:
    from __future__ import annotations
    from typing import ClassVar
except ImportError:
    pass

from mcp23017 import VirtualPin

PULL_HIGH = True
ON = False
OFF = True


class Motor:
    def __init__(
        self,
        *,
        motor: VirtualPin,
        straight: list[VirtualPin],
        diverging: list[VirtualPin],
    ):
        self._motor = motor
        self._straight = straight
        self._diverging = diverging
        for pin in self._straight:
            pin.input(PULL_HIGH)
        for pin in self._diverging:
            pin.input(PULL_HIGH)
        if self.straight:
            self.set_straight()
        elif self.diverging:
            self.set_diverging()

    @property
    def straight(self):
        return all(not pin.value() for pin in self._straight) and all(
            pin.value() for pin in self._diverging
        )

    def set_straight(self):
        self._motor.output(ON)

    @property
    def diverging(self):
        return all(not pin.value() for pin in self._diverging) and all(
            pin.value() for pin in self._straight
        )

    def set_diverging(self):
        self._motor.output(OFF)

    @property
    def state(self):
        if self.straight:
            return "straight"
        if self.diverging:
            return "diverging"
        return None


class Switch:
    def __init__(
        self, *, switch: VirtualPin, led: VirtualPin, config: dict[Motor, bool]
    ):
        self.switch = switch
        self.switch.input(PULL_HIGH)
        self.led = led
        self.config = config
        self._last_time = 0
        self._last_state = self.current_state
        self.led.output(self.current_state)

    def push(self):
        for motor, diverging in self.config.items():
            if diverging:
                motor.set_diverging()
            else:
                motor.set_straight()

    def poll_switch(self):
        if not self.switch.value():
            self.push()

    @property
    def current_state(self) -> bool:
        return all(
            motor.state == ("diverging" if diverging else "straight")
            for motor, diverging in self.config.items()
        )

    @property
    def state(self) -> bool:
        current_state = self.current_state
        # Currently reading zero
        if not current_state:
            # reset 'last time active'
            self._last_time = 0
            # current state is false
            self._last_state = False
        else:
            # Currently active
            if not self._last_state:
                # But previously inactive
                if self._last_time == 0:
                    # Last time was not active - record new active time
                    self._last_time = time.time()
                elif (time.time() - self._last_time) > 0.5:
                    # First active old enough, set new last state
                    self._last_state = True
        return self._last_state

    def poll_state(self):
        self.led.output(self.state)


class Base:

    instances: ClassVar[list[Base]] = []

    def __init__(self, *, switches: list[Switch]):
        self.switches = switches
        self.__class__.instances.append(self)

    def poll_switches(self):
        for switch in self.switches:
            switch.poll_switch()

    def poll_state(self):
        for switch in self.switches:
            switch.poll_state()

    @classmethod
    def poll_all_switches(cls):
        for instance in cls.instances:
            instance.poll_switches()

    @classmethod
    def poll_all_states(cls):
        for instance in cls.instances:
            instance.poll_state()

    def debug(self):
        for k, v in self.__dict__.items():
            if isinstance(v, Motor):
                print(k)
                print("straight: ", [(p._pin, p.value()) for p in v._straight])
                print("diverging: ", [(p._pin, p.value()) for p in v._diverging])


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
        led_diverging: VirtualPin,
    ):

        self.motor = Motor(
            motor=motor,
            straight=[sensor_straight],
            diverging=[sensor_diverging],
        )

        self.switch_straight = Switch(
            switch=switch_straight, led=led_straight, config={self.motor: False}
        )

        self.switch_diverging = Switch(
            switch=switch_diverging, led=led_diverging, config={self.motor: True}
        )

        super().__init__(
            switches=[self.switch_straight, self.switch_diverging],
        )


class PairedTurnout(Base):
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
        led_diverging: VirtualPin,
    ):

        self.motor = Motor(
            motor=motor,
            straight=[sensor1_straight, sensor2_straight],
            diverging=[sensor1_diverging, sensor2_diverging],
        )

        self.switch_straight = Switch(
            switch=switch_straight, led=led_straight, config={self.motor: False}
        )
        self.switch_diverging = Switch(
            switch=switch_diverging, led=led_diverging, config={self.motor: True}
        )

        super().__init__(
            switches=[self.switch_straight, self.switch_diverging],
        )


class Crossover(Base):
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
        sensor3_diverging: VirtualPin,
        sensor4_straight: VirtualPin,
        sensor4_diverging: VirtualPin,
    ):

        self.motor1 = Motor(
            motor=motor1,
            straight=[sensor1_straight, sensor4_straight],
            diverging=[sensor1_diverging, sensor4_diverging],
        )
        self.motor2 = Motor(
            motor=motor2,
            straight=[sensor2_straight, sensor3_straight],
            diverging=[sensor2_diverging, sensor3_diverging],
        )

        self.switch_straight = Switch(
            switch=switch_straight,
            led=led_straight,
            config={self.motor1: False, motor2: False},
        )
        self.switch_diverging = Switch(
            switch=switch_diverging,
            led=led_diverging,
            config={self.motor1: True, motor2: True},
        )
        self.switch_partial = Switch(
            switch=switch_partial,
            led=led_partial,
            config={self.motor1: True, self.motor2: False},
        )

        super().__init__(
            switches=[self.switch_straight, self.switch_partial, self.switch_diverging],
        )


class Sidings(Base):
    def __init__(
        self,
        *,
        motor1: VirtualPin,
        motor2: VirtualPin,
        motor3: VirtualPin,
        motor4: VirtualPin,
        switch1: VirtualPin,
        switch2: VirtualPin,
        switch3: VirtualPin,
        switch4: VirtualPin,
        switch5: VirtualPin,
        led1: VirtualPin,
        led2: VirtualPin,
        led3: VirtualPin,
        led4: VirtualPin,
        led5: VirtualPin,
        sensor1_straight: VirtualPin,
        sensor1_diverging: VirtualPin,
        sensor2_straight: VirtualPin,
        sensor2_diverging: VirtualPin,
        sensor3_straight: VirtualPin,
        sensor3_diverging: VirtualPin,
        sensor4_straight: VirtualPin,
        sensor4_diverging: VirtualPin,
    ):

        self.motor1 = Motor(
            motor=motor1,
            straight=[sensor1_straight],
            diverging=[sensor1_diverging],
        )
        self.motor2 = Motor(
            motor=motor2,
            straight=[sensor2_straight],
            diverging=[sensor2_diverging],
        )
        self.motor3 = Motor(
            motor=motor3,
            straight=[sensor3_straight],
            diverging=[sensor3_diverging],
        )
        self.motor4 = Motor(
            motor=motor4,
            straight=[sensor4_straight],
            diverging=[sensor4_diverging],
        )

        self.switch1 = Switch(
            switch=switch1, led=led1, config={self.motor1: True, self.motor2: True}
        )
        self.switch2 = Switch(
            switch=switch2,
            led=led2,
            config={self.motor1: True, self.motor2: False, self.motor3: True},
        )
        self.switch3 = Switch(
            switch=switch3,
            led=led3,
            config={self.motor1: True, self.motor2: False, self.motor3: False},
        )
        self.switch4 = Switch(
            switch=switch4, led=led4, config={self.motor1: False, self.motor4: False}
        )
        self.switch5 = Switch(
            switch=switch5, led=led5, config={self.motor1: False, self.motor4: True}
        )

        super().__init__(
            switches=[
                self.switch1,
                self.switch2,
                self.switch3,
                self.switch4,
                self.switch5,
            ],
        )
