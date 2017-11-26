import timeit
import platform
import unittest
from pathlib import Path

from .simulator import Simulator


class ATS(Simulator):
    """ Derived class holding OS dependent paths to American Truck Simulator (ATS) game files """
    if platform.system() == 'Darwin':
        RootGameFolder = Path('~/Library/Application Support/Steam/steamapps/common/American Truck Simulator').expanduser()
        UserGameFolder = Path('~/Library/Application Support/American Truck Simulator').expanduser()
        GameExecutable = RootGameFolder / 'American Truck Simulator.app/Contents/MacOS/amtrucks'
        TelemetryPlugin = Path(__file__).parent / 'telemetry/plugin/libautodrome.so'
    if platform.system() == 'Linux':
        RootGameFolder = Path('~/.steam/steam/steamapps/common/American Truck Simulator').expanduser()
        UserGameFolder = Path('~/local/share/American Truck Simulator').expanduser()
        GameExecutable = RootGameFolder / 'bin/amtrucks'
        TelemetryPlugin = Path(__file__).parent / 'telemetry/plugin/todo.so'
    if platform.system() == 'Windows':
        RootGameFolder = Path('C:/Program Files (x86)/Steam/steamapps/common/American Truck Simulator')
        UserGameFolder = Path('~/Documents/American Truck Simulator').expanduser()
        GameExecutable = RootGameFolder / 'bin/amtrucks.exe'
        TelemetryPlugin = Path(__file__).parent / 'telemetry/plugin/todo.dll'
    SteamAppID = 270880
    MapsFolder = Path(__file__).parent / '../maps/ets2/'


# region Unit Tests


class TestATS(unittest.TestCase):
    RepeatFPS = 100
    MinimumFPS = 20

    @unittest.skipUnless(ATS.RootGameFolder.exists(), "ATS not installed")
    def test_capture(self):
        with ATS() as ats:
            ats.command('preview indy500')
            seconds = timeit.timeit(lambda: ats.frame(ats.telemetry.data()), number=self.RepeatFPS)
        self.assertGreater(self.RepeatFPS / seconds, self.MinimumFPS)


# endregion
