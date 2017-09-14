import time
import timeit
import unittest
import platform
import warnings
import contextlib
import subprocess
import numpy as np
import Cocoa as CA
import Quartz.CoreGraphics as CG

from .window import Window


class WindowDarwin(Window):
    """ Abstract window class for capture of game window content on macOS """
    TitleBarHeight = 22

    def __init__(self, pid: int, timeout: float):
        """ Create a new instance from main application window of a process """
        super().__init__(pid, timeout)
        deadline = time.time() + timeout
        while True:
            if time.time() > deadline:
                raise WindowDarwinError("Main process window not found")
            options = CG.kCGWindowListOptionAll
            relativeToWindow = CG.kCGNullWindowID
            windows = CG.CGWindowListCopyWindowInfo(options, relativeToWindow)
            if windows is None:
                time.sleep(0.1)
                continue
            windows = [window for window in windows if window['kCGWindowOwnerPID'] == pid]
            if len(windows) == 0:
                time.sleep(0.1)
                continue
            if windows[0]['kCGWindowBounds'] == {'X': 0, 'Y': 0, 'Width': 0, 'Height': 0}:
                time.sleep(0.1)
                continue
            break
        self.window = windows[0]

    def activate(self):
        """ Bring window to foreground """
        runningApplication = CA.NSRunningApplication.runningApplicationWithProcessIdentifier_(self.pid)
        activationOptions = CA.NSApplicationActivateAllWindows | CA.NSApplicationActivateIgnoringOtherApps
        runningApplication.activateWithOptions_(activationOptions)

    def capture(self) -> np.array:
        """ Capture border-less window content and return it as a raw pixel array """
        screenBounds = CG.CGRectNull
        listOption = CG.kCGWindowListOptionIncludingWindow
        windowID = self.window['kCGWindowNumber']
        imageOption = CG.kCGWindowImageBoundsIgnoreFraming | CG.kCGWindowImageShouldBeOpaque
        screenshot = CG.CGWindowListCreateImage(screenBounds, listOption, windowID, imageOption)

        width, height = CG.CGImageGetWidth(screenshot), CG.CGImageGetHeight(screenshot)
        bytesPerRow = CG.CGImageGetBytesPerRow(screenshot)

        if width <= 1 and height <= 1:
            warnings.warn("Can't capture window because the process is minimized", RuntimeWarning)
            return None

        dataProvider = CG.CGImageGetDataProvider(screenshot)
        rawPixels = CG.CGDataProviderCopyData(dataProvider)
        image = np.frombuffer(rawPixels, dtype=np.uint8).reshape([height, bytesPerRow // 4, 4])

        return image[self.TitleBarHeight:height, 0:width, 0:3]


class WindowDarwinError(Exception):
    """ Exception that is raised in case of a failed WindowDarwin class instance """
    pass


# region Unit Tests


@unittest.skipUnless(platform.system() == 'Darwin', "Only for macOS")
class TestWindowDarwin(unittest.TestCase):
    GuineaPigApplication = ['/Applications/Calculator.app/Contents/MacOS/Calculator']
    RepeatFPS = 100
    MinimumFPS = 50

    def test_capture(self):
        with subprocess.Popen(self.GuineaPigApplication) as process:
            window = self.wait_for_gui(process, timeout=10)
            pixels = window.capture()
            process.terminate()
        self.assertIsInstance(pixels, np.ndarray)

    def test_performance(self):
        with subprocess.Popen(self.GuineaPigApplication) as process:
            window = self.wait_for_gui(process, timeout=10)
            seconds = timeit.timeit(lambda: window.capture(), number=self.RepeatFPS)
            process.terminate()
        self.assertGreater(self.RepeatFPS / seconds, self.MinimumFPS)

    def wait_for_gui(self, process: subprocess.Popen, timeout: int=0):
        deadline = time.time() + timeout
        while time.time() <= deadline:
            with contextlib.suppress(WindowDarwinError):
                return WindowDarwin(pid=process.pid)
        process.terminate()
        raise TimeoutError("Timeout while waiting for application window")


# endregion
