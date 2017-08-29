import abc
import numpy as np


class Window(abc.ABC):
    """ Abstract class for capturing content of a window """
    def __init__(self, pid: int):
        """ Create a new instance from main application window of a process """
        self.pid = pid

    def activate(self):
        """ Bring window to foreground """
        raise NotImplementedError

    def capture(self) -> np.array:
        """ Capture border-less window content and return it as a raw pixel array """
        raise NotImplementedError
