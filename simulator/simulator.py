import abc
import time
import shutil
import subprocess
from pathlib import Path
import distutils.dir_util as dstdir

from .window import Window
from .controller import Keyboard


class Simulator(abc.ABC):
    """ Abstract interface for launching and controlling ETS2/ATS simulation games """
    RootGameFolder = Path()
    UserGameFolder = Path()
    GameExecutable = Path()
    TelemetryPlugin = Path()
    SteamAppID = None
    MapsFolder = Path()
    SettingsFolder = Path()
    Config = {'g_developer': '1', 'g_console': '1',
              'r_fullscreen': '0', 'r_mode_width': '2048', 'r_mode_height': '1024'}

    def __init__(self):
        self.steam1_file = Path.cwd() / 'steam_appid.txt'
        self.steam2_file = self.GameExecutable.parent / 'steam_appid.txt'
        self.config_file = self.UserGameFolder / 'config.cfg'
        self.mod_dir = self.UserGameFolder / 'mod' / 'autodrome'

        self.process = None
        self.window = None
        self.keyboard = None

    def start(self):
        """ Setup and start the simulator process """
        self.setup_telemetry(self.TelemetryPlugin)
        self.setup_maps(self.mod_dir, self.MapsFolder)
        self.setup_config(self.config_file, self.Config)
        self.setup_steam(self.steam1_file)
        self.setup_steam(self.steam2_file)

        print("Starting game process '{}'...".format(self.GameExecutable))
        game_command = [str(self.GameExecutable), '-nointro', '-force_mods', '-noworkshop', '-window_pos', '0', '0']
        self.process = subprocess.Popen(game_command)
        time.sleep(5)  # FIXME: Wait to receive ZMQ telemetry 'init' event message instead of sleep
        self.window = Window(pid=self.process.pid)
        self.keyboard = Keyboard()

        self.window.activate()
        self.enter()  # Get rid of pesky Telemetry SDK warning

    def __enter__(self):
        self.start()
        return self

    @classmethod
    def setup_maps(cls, mod_dir: Path, local_dir: Path):
        """ Copy local mod with custom map into the ATS/ETS2 mod folder """
        print("Setting up mod with map in '{}'...".format(mod_dir))
        mod_dir.mkdir(parents=True, exist_ok=True)
        dstdir.copy_tree(str(local_dir), str(mod_dir))

    @classmethod
    def setup_telemetry(cls, telemetry_lib: Path):
        """ Copy Telemetry SDK library into ATS/ETS2 telemetry folder """
        destination_dir = cls.GameExecutable.parent / 'plugins'
        print("Setting up telemetry plugin in '{}'...".format(destination_dir))
        destination_dir.mkdir(exist_ok=True)
        shutil.copy(telemetry_lib, destination_dir)

    @classmethod
    def setup_config(cls, config_file: Path, override: dict) -> None:
        """ Override existing ATS/ETS2 config file with the provided keys and values """
        print("Setting up game configuration in '{}'".format(config_file))
        old_lines = config_file.read_text().splitlines()
        override = override.copy()
        new_lines = []

        for line in old_lines:
            words = line.split()
            if len(words) > 1 and words[1] in override:
                key, value = words[1], override[words[1]]
                new_lines.append('uset {key} "{value}"'.format(key=key, value=value))
                del override[key]
            else:
                new_lines.append(line)
        for key, value in override.items():
            new_lines.append('uset {key} "{value}"'.format(key=key, value=value))

        config_file.write_text('\n'.join(new_lines))

    @classmethod
    def setup_steam(cls, steam_file: Path) -> None:
        """ Setup a special Steam file
        This little trick of creating 'steam_appid.txt' file with the Steam AppID prevents
        SteamAPI_RestartAppIfNecessary(...) API call that would start a new process by forking
        the Steam client application over which we would have no control.

        Details: https://partner.steamgames.com/doc/api/steam_api#SteamAPI_RestartAppIfNecessary """
        print("Setting up Steam ID in '{}'".format(steam_file))
        steam_file.write_text(str(cls.SteamAppID))

    def control(self, steer: int, acceleration: int):
        """ Issue steering and throttle/brake commands """
        self.window.activate()
        if steer == 0:
            self.keyboard.release('→')
            self.keyboard.release('←')
        if steer > 0:
            self.keyboard.press('→')
        if steer < 0:
            self.keyboard.press('←')
        if acceleration == 0:
            self.keyboard.release('↑')
            self.keyboard.release('↓')
        if acceleration > 0:
            self.keyboard.press('↑')
        if acceleration < 0:
            self.keyboard.press('↓')

    def command(self, command: str, wait: float=0):
        """ Type command into the game developer console
        List of Commands: http://modding.scssoft.com/wiki/Documentation/Engine/Console/Commands """
        self.window.activate()
        if self.process and self.keyboard:
            self.keyboard.type('~')
            time.sleep(0.1)
            self.keyboard.type(command)
            self.enter()
            time.sleep(wait)

    def enter(self):
        """ Press enter key ¯\_(ツ)_/¯ """
        self.keyboard.press('\n')
        time.sleep(0.1)
        self.keyboard.release('\n')

    def terminate(self):
        """ Stop the simulator process and clean up """
        try:
            self.steam1_file.unlink()
            self.steam2_file.unlink()
        except FileNotFoundError:
            pass
        self.keyboard = None
        self.window = None
        self.process.terminate()
        self.process.wait(timeout=0.1)
        self.process = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
