import platform

from .controller import KeyboardABC, SteeringWheelABC


if platform.system() == 'Darwin':
    from .darwin import SteeringWheelDarwin as SteeringWheel, KeyboardDarwin as Keyboard
else:
    raise NotImplementedError
