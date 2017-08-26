import abc
import time
import timeit
import unittest
import argparse
import platform
import subprocess
from pathlib import Path

from window import Window


class SimulatorABC(abc.ABC):
    """ Abstract interface for launching and controlling ATS/ETS2 simulation games """
    RootGameFolder = Path()
    UserGameFolder = Path()
    GameExecutable = Path()
    SteamAppID = None
    SCSExtractorExecutable = Path('simulator/bin/scs_extractor.exe')
    Config = {'g_developer': '1', 'g_console': '1',
              'r_fullscreen': '0', 'r_mode_width': '1024', 'r_mode_height': '576'}

    def __init__(self):
        self.steam1_file = Path.cwd() / 'steam_appid.txt'
        self.steam2_file = self.GameExecutable.parent / 'steam_appid.txt'
        self.config_file = self.UserGameFolder / 'config.cfg'
        self.process = None
        self.window = None

    def __enter__(self):
        """ Start the simulator process """
        self.set_config(self.config_file, self.Config)
        self.set_steam(self.steam1_file, self.SteamAppID)
        self.set_steam(self.steam2_file, self.SteamAppID)
        try:
            self.process = subprocess.Popen([str(self.GameExecutable), '-nointro', '-force_mods'])
            time.sleep(5)  # FIXME: Wait to receive ZMQ telemetry event message
            self.window = Window(pid=self.process.pid)
        except Exception:
            self.window = None
            self.process.terminate()
            return None
        finally:
            return self

    def __exit__(self, type, value, traceback):
        """ Stop the simulator process """
        self.window = None
        self.process.terminate()
        self.steam1_file.unlink()
        self.steam2_file.unlink()


    @classmethod
    def extract(cls):
        """ Extract game files (*.scs) inside of the game root directory """
        for file, directory in [('base.scs', 'base'), ('def.scs', 'def')]:
            if (cls.RootGameFolder / directory).exists():
                continue
            extractor = cls.SCSExtractorExecutable
            archive = cls.RootGameFolder / file
            destination = cls.RootGameFolder / directory
            if platform.system() == 'Windows':
                arguments = [extractor, archive, destination]
            else:
                arguments = ['wineconsole', extractor, archive, destination]
            subprocess.check_call(arguments)

    @classmethod
    def set_steam(cls, file: Path, appid: int):
        """ Setup a special Steam file
        This little trick of creating 'steam_appid.txt' file with the Steam AppID prevents
        SteamAPI_RestartAppIfNecessary(...) API call that would start a new process by forking
        the Steam client application over which we would have no control.

        Details: https://partner.steamgames.com/doc/api/steam_api#SteamAPI_RestartAppIfNecessary """
        file.write_text(str(appid))

    @classmethod
    def set_config(cls, file: Path, config: dict):
        """ Modify existing ATS/ETS2 config file with the provided keys and values """
        old_lines = file.read_text().splitlines()
        config = config.copy()
        new_lines = []

        for line in old_lines:
            words = line.split()
            if len(words) > 1 and words[1] in config:
                key, value = words[1], config[words[1]]
                new_lines.append('uset {key} "{value}"'.format(key=key, value=value))
                del config[key]
            else:
                new_lines.append(line)
        for key, value in config.items():
            new_lines.append('uset {key} "{value}"'.format(key=key, value=value))

        file.write_text('\n'.join(new_lines))


class ETS2(SimulatorABC):
    """ Derived class holding OS dependent paths to Euro Truck Simulator 2 (ETS2) game files """
    if platform.system() == 'Darwin':
        RootGameFolder = Path('~/Library/Application Support/Steam/steamapps/common/Euro Truck Simulator 2').expanduser()
        UserGameFolder = Path('~/Library/Application Support/Euro Truck Simulator 2').expanduser()
        GameExecutable = RootGameFolder / 'Euro Truck Simulator 2.app/Contents/MacOS/eurotrucks2'
    if platform.system() == 'Linux':
        RootGameFolder = Path('~/.steam/steam/steamapps/common/Euro Truck Simulator 2').expanduser()
        UserGameFolder = Path('~/local/share/Euro Truck Simulator 2').expanduser()
        GameExecutable = RootGameFolder / 'bin/eurotrucks2'
    if platform.system() == 'Windows':
        RootGameFolder = Path('C:/Program Files (x86)/Steam/steamapps/common/Euro Truck Simulator 2')
        UserGameFolder = Path('~/Documents/Euro Truck Simulator 2').expanduser()
        GameExecutable = RootGameFolder / 'bin/eurotrucks2.exe'
    SteamAppID = 227300


class ATS(SimulatorABC):
    """ Derived class holding OS dependent paths to American Truck Simulator (ATS) game files """
    if platform.system() == 'Darwin':
        RootGameFolder = Path('~/Library/Application Support/Steam/steamapps/common/American Truck Simulator').expanduser()
        UserGameFolder = Path('~/Library/Application Support/American Truck Simulator').expanduser()
        GameExecutable = RootGameFolder / 'American Truck Simulator.app/Contents/MacOS/amtrucks'
    if platform.system() == 'Linux':
        RootGameFolder = Path('~/.steam/steam/steamapps/common/American Truck Simulator').expanduser()
        UserGameFolder = Path('~/local/share/American Truck Simulator').expanduser()
        GameExecutable = RootGameFolder / 'bin/amtrucks'
    if platform.system() == 'Windows':
        RootGameFolder = Path('C:/Program Files (x86)/Steam/steamapps/common/American Truck Simulator')
        UserGameFolder = Path('~/Documents/American Truck Simulator').expanduser()
        GameExecutable = RootGameFolder / 'bin/amtrucks.exe'
    SteamAppID = 270880


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ATS/ETS2 as a Self-Driving Car Simulator")
    parser.add_argument('-g', '--game', help="Game to run", choices=['ATS', 'ETS2'], default='ATS')
    args = parser.parse_args()

    constructors = {'ATS': ATS, 'ETS2': ETS2}
    with constructors[args.game]() as simulator:
        while simulator.process.poll() is None:
            time.sleep(1)


# region Unit Tests


class TestSimulator(unittest.TestCase):
    RepeatFPS = 100
    MinimumFPS = 50

    @unittest.skipUnless(ATS.RootGameFolder.exists(), "ATS not installed")
    def test_ATS(self):
        with ATS() as ats:
            seconds = timeit.timeit(lambda: ats.window.capture(), number=self.RepeatFPS)
            self.assertGreater(self.RepeatFPS / seconds, self.MinimumFPS)
        time.sleep(1)

    @unittest.skipUnless(ETS2.RootGameFolder.exists(), "ETS2 not installed")
    def test_ETS2(self):
        with ETS2() as ets2:
            seconds = timeit.timeit(lambda: ets2.window.capture(), number=self.RepeatFPS)
            self.assertGreater(self.RepeatFPS / seconds, self.MinimumFPS)
        time.sleep(1)


# endregion
