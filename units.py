import time


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
        self._straight = [DebouncedPin(straight) for straight in straight]
        self._diverging = [DebouncedPin(diverging) for diverging in diverging]
        self._motor.output(self.straight)

    @property
    def straight(self):
        return all(self._straight) and not all(self._diverging)

    def set_straight(self):
        self._motor.output(ON)

    @property
    def diverging(self):
        return all(self._diverging) and not all(self._straight)

    def set_diverging(self):
        self._motor.output(OFF)


class Switch:
    def __init__(
        self, *, switch: VirtualPin, led: VirtualPin, config: dict[Motor, bool]
    ):
        self.switch = switch
        self.switch.input(PULL_HIGH)
        self.led = led
        self.config = config

    def poll_switch(self):
        if not self.switch.value():
            for motor, diverging in self.config.items():
                if diverging:
                    motor.set_diverging()
                else:
                    motor.set_straight()

    def poll_state(self):
        self.led.output(
            all(
                getattr(motor, "diverging" if diverging else "straight")
                for motor, diverging in self.config.items()
            )
        )


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
        if self._pin.value() == 0:
            if self._last_time == 0:
                self._last_time = time.time()
            elif (time.time() - self._last_time) > self._threshold:
                self._value = True
        else:
            self._value = False


class Base:
    def __init__(self, *, switches: list[Switch]):
        self.switches = switches

    def poll_switches(self):
        for switch in self.switches:
            switch.poll_switch()

    def poll_state(self):
        for switch in self.switches:
            switch.poll_state()


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

        motor = Motor(
            motor=motor,
            straight=[sensor_straight],
            diverging=[sensor_diverging],
        )

        switch_straight = Switch(
            switch=switch_straight, led=led_straight, config={motor: False}
        )

        switch_diverging = Switch(
            switch=switch_diverging, led=led_diverging, config={motor: True}
        )

        super().__init__(
            switches=[switch_straight, switch_diverging],
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

        motor = Motor(
            motor=motor,
            straight=[sensor1_straight, sensor2_straight],
            diverging=[sensor1_diverging, sensor2_diverging],
        )

        switch_straight = Switch(
            switch=switch_straight, led=led_straight, config={motor: False}
        )
        switch_diverging = Switch(
            switch=switch_diverging, led=led_diverging, config={motor: True}
        )

        super().__init__(
            switches=[switch_straight, switch_diverging],
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
    ):

        motor1 = Motor(
            motor=motor1,
            straight=[sensor1_straight, sensor3_straight],
            diverging=[sensor1_diverging, sensor3_diverging],
        )
        motor2 = Motor(
            motor=motor2,
            straight=[sensor2_straight],
            diverging=[sensor2_diverging],
        )

        switch_straight = Switch(
            switch=switch_straight,
            led=led_straight,
            config={motor1: False, motor2: False},
        )
        switch_diverging = Switch(
            switch=switch_diverging,
            led=led_diverging,
            config={motor1: True, motor2: True},
        )
        switch_partial = Switch(
            switch=switch_partial, led=led_partial, config={motor1: True, motor2: False}
        )

        super().__init__(
            switches=[switch_straight, switch_partial, switch_diverging],
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

        motor1 = Motor(
            motor=motor1, straight=[sensor1_straight], diverging=[sensor1_diverging]
        )
        motor2 = Motor(
            motor=motor2, straight=[sensor2_straight], diverging=[sensor2_diverging]
        )
        motor3 = Motor(
            motor=motor3, straight=[sensor3_straight], diverging=[sensor3_diverging]
        )
        motor4 = Motor(
            motor=motor4, straight=[sensor4_straight], diverging=[sensor4_diverging]
        )

        switch1 = Switch(switch=switch1, led=led1, config={motor1: True, motor2: True})
        switch2 = Switch(
            switch=switch2, led=led2, config={motor1: True, motor2: False, motor3: True}
        )
        switch3 = Switch(
            switch=switch3,
            led=led3,
            config={motor1: True, motor2: False, motor3: False},
        )
        switch4 = Switch(
            switch=switch4, led=led4, config={motor1: False, motor4: False}
        )
        switch5 = Switch(switch=switch5, led=led5, config={motor1: False, motor4: True})

        super().__init__(
            switches=[switch1, switch2, switch3, switch4, switch5],
        )
