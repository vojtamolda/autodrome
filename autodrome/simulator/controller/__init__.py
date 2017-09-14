import platform


if platform.system() == 'Darwin':
    from .darwin import SteeringWheelDarwin as SteeringWheel, KeyboardDarwin as Keyboard
else:
    from .controller import SteeringWheel, Keyboard
