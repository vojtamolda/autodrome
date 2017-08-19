import abc


class SteeringWheelABC(abc.ABC):
    """ Abstract controller class for interfacing with virtual steering wheels """
    class Axis:
        """ Controller axis helper for converting raw binary values
        The axis value is always stored as a raw integer and on the fly converted to/fom a floating point value. """
        def __init__(self, value: float = 0, range: tuple = (-1, +1), raw_range: tuple = (0, 255)):
            self.range = range
            self.span = range[1] - range[0]
            self.raw_range = raw_range
            self.raw_span = raw_range[1] - raw_range[0]
            self.raw = None
            self.value = value

        @property
        def value(self) -> float:
            """ Get value of the controller axis position """
            relative = (self.raw - self.raw_range[0]) / self.raw_span
            value = self.range[0] + relative * self.span
            value = max(value, self.range[0])
            value = min(value, self.range[1])
            return value

        @value.setter
        def value(self, new_value: float):
            """ Set value of the controller axis position and clip it if not within range """
            new_value = max(new_value, self.range[0])
            new_value = min(new_value, self.range[1])
            relative = (new_value - self.range[0]) / self.span
            self.raw = self.raw_range[0] + round(relative * self.raw_span)

    steer = Axis(0.0, range=(-1, +1))
    throttle = Axis(0.0, range=(0, +1))
    brake = Axis(0.0, range=(0, +1))
    clutch = Axis(0.0, range=(0, +1))

    def send(self):
        """ Send the current steer, throttle and brake values to the virtual controller """
        raise NotImplementedError


class KeyboardABC(abc.ABC):
    """ Abstract controller class for interfacing with virtual keyboards """
    def type(self, string: str):
        """ Type string on the virtual keyboard """
        for key in string:
            self.press(key)
            self.release(key)

    def press(self, key: str):
        """ Press a virtual keyboard key """
        raise NotImplementedError

    def release(self, key: str):
        """ Release a virtual keyboard key """
        raise NotImplementedError
