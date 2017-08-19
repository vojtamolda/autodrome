import platform

from .window import WindowABC


if platform.system() == 'Darwin':
    from .darwin import WindowDarwin as Window
else:
    raise NotImplementedError
