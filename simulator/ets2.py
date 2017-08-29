import timeit
import platform
import unittest
from pathlib import Path

from .simulator import Simulator


class ETS2(Simulator):
    """ Derived class holding OS dependent paths to Euro Truck Simulator 2 (ETS2) game files """
    if platform.system() == 'Darwin':
        RootGameFolder = Path('~/Library/Application Support/Steam/steamapps/common/Euro Truck Simulator 2').expanduser()
        UserGameFolder = Path('~/Library/Application Support/Euro Truck Simulator 2').expanduser()
        GameExecutable = RootGameFolder / 'Euro Truck Simulator 2.app/Contents/MacOS/eurotrucks2'
        TelemetryPlugin = Path('./simulator/telemetry/plugin/libautodrome.so')
    if platform.system() == 'Linux':
        RootGameFolder = Path('~/.steam/steam/steamapps/common/Euro Truck Simulator 2').expanduser()
        UserGameFolder = Path('~/local/share/Euro Truck Simulator 2').expanduser()
        GameExecutable = RootGameFolder / 'bin/eurotrucks2'
        TelemetryPlugin = Path('./simulator/telemetry/plugin/todo.so')
    if platform.system() == 'Windows':
        RootGameFolder = Path('C:/Program Files (x86)/Steam/steamapps/common/Euro Truck Simulator 2')
        UserGameFolder = Path('~/Documents/Euro Truck Simulator 2').expanduser()
        GameExecutable = RootGameFolder / 'bin/eurotrucks2.exe'
        TelemetryPlugin = Path('./simulator/telemetry/plugin/todo.dll')
    SteamAppID = 227300
    MapsFolder = Path('./maps/ets2/')
    SettingsFolder = Path('~/.autodrome/ets2/').expanduser()


# region Unit Tests


class TestETS2(unittest.TestCase):
    RepeatFPS = 100
    MinimumFPS = 25

    @unittest.skipUnless(ETS2.RootGameFolder.exists(), "ETS2 not installed")
    def test_capture(self):
        with ETS2() as ets2:
            ets2.command('preview europe', wait=10)
            seconds = timeit.timeit(lambda: ets2.window.capture(), number=self.RepeatFPS)
        self.assertGreater(self.RepeatFPS / seconds, self.MinimumFPS)


# endregion
