import platform


if platform.system() == 'Darwin':
    from .darwin import WindowDarwin as Window
else:
    from .window import Window
