import shutil
import unittest
import platform
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt

from ..simulator import Simulator

from .map import Map
from .definition import Definition


class Policeman:
    ExtractorExecutable = Path('simulator/bin/scs_extractor.exe')

    def __init__(self, simulator: Simulator):
        self.simulator = simulator
        self.map = Map(simulator.MapsFolder / 'map' / 'indy500.txt')
        self.world = Definition(simulator.SettingsFolder / 'cache' / 'def.scs' / 'world', recursive=True)

    def setup_cache(self, overwrite: bool=False) -> None:
        """ Extract ETS2/ATS archives to an intermediate cache for parsing """
        extractor = self.simulator.RootGameFolder / 'scs_extractor.exe'
        shutil.copy(self.ExtractorExecutable, extractor)

        cache_dir = self.simulator.SettingsFolder / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        print("Setting up extracted game archives cache in '{}'...".format(cache_dir))

        for archive in ['def.scs']:  # It looks like base.scs and others are not needed
            destination_dir = cache_dir / archive
            if overwrite is False and destination_dir.is_dir():
                continue
            destination_dir.mkdir(parents=True, exist_ok=True)
            print("Extracting '{}' (This takes a few minutes)...".format(self.simulator.RootGameFolder / archive))
            if platform.system() == 'Windows':
                extract_command = [str(extractor), archive, str(destination_dir)]
            else:
                extract_command = ['wineconsole', str(extractor), archive, str(destination_dir)]
            subprocess.check_call(extract_command, cwd=self.simulator.RootGameFolder)
        extractor.unlink()

    def plot(self):
        xnodes = [node['position']['x'] for node in self.map['nodes'].values()]
        ynodes = [node['position']['z'] for node in self.map['nodes'].values()]

        figure = plt.figure()
        axes = plt.axes(xlim=(1.1 * min(xnodes), 1.1 * max(xnodes)), ylim=(1.1 * min(ynodes), 1.1 * max(ynodes)))
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        nodes = axes.plot(xnodes, ynodes, 'o', lw=1)[0]
        agent = axes.plot([], [], 'x', lw=2)[0]
        plt.show()


# region Unit Tests


class TestPoliceman(unittest.TestCase):

    def test_plot(self):
        policeman = Policeman(ATS)
        policeman.plot()
        pass


# endregion
