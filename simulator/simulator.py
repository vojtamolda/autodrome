import abc
import time
import unittest
import platform
import subprocess
from pathlib import Path


class SimulatorABC(abc.ABC):
    """ Abstract interface for launching and controlling ATS/ETS2 simulation games """
    RootGameFolder = Path()
    UserGameFolder = Path()
    GameExecutable = Path()
    SteamAppID = None
    SCSExtractorExecutable = Path('simulator/bin/scs_extrator.exe')

    def __init__(self):
        self.steam_file = Path.cwd() / 'steam_appid.txt'
        self.process = None

    def start(self):
        """ Start the simulator process
        The dirty little trick of creating 'steam_appid.txt' file with the Steam AppID prevents
        SteamAPI_RestartAppIfNecessary(...) client API call to spawn a new process.
        Details: https://partner.steamgames.com/doc/api/steam_api#SteamAPI_RestartAppIfNecessary """
        self.enable_developer_console()
        self.steam_file.write_text(str(self.SteamAppID))
        self.process = subprocess.Popen(str(self.GameExecutable))

    def stop(self):
        """ Stop the simulator process """
        self.process.terminate()
        self.steam_file.unlink()

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
    def enable_developer_console(cls):
        """ Modify 'g_developer' and 'g_console' settings in the user config file to enable developer console. """
        cfg_keys, cfg_lines = {'g_developer', 'g_console'}, []
        with open(str(cls.UserGameFolder / 'config.cfg'), 'r') as cfg_file:
            for cfg_line in cfg_file.readlines():
                words = cfg_line.split()
                if len(words) > 1 and words[1] in cfg_keys:
                    cfg_lines.append('{words[0]} {words[1]} "1"'.format(words=words))
                    cfg_keys.remove(words[1])
                else:
                    cfg_lines.append(cfg_line)

        for key in cfg_keys:
            cfg_lines.append('uset ' + key + ' "1"')

        with open(str(cls.UserGameFolder / 'config.cfg'), 'w') as cfg_file:
            cfg_file.writelines(cfg_lines)


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


# region Unit Tests


class TestSimulator(unittest.TestCase):

    @unittest.skipIf(not ATS.RootGameFolder.exists(), "ATS is not installed")
    def test_ATS(self):
        ats = ATS()
        ats.start()
        time.sleep(10)
        ats.stop()

    @unittest.skipIf(not ETS2.RootGameFolder.exists(), "ETS2 not installed")
    def test_ETS2(self):
        ets2 = ETS2()
        ets2.start()
        time.sleep(10)
        ets2.stop()


# endregion
