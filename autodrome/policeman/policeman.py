import pickle
import shutil
import unittest
import platform
import subprocess
from pathlib import Path

from autodrome.simulator import Simulator, ETS2, ATS

from .map import Map
from .definition import Definition


class Policeman:
    ExtractorExecutable = Path(__file__).parent / 'bin/scs_extractor.exe'

    def __init__(self, simulator: Simulator):
        self.simulator = simulator
        self.world = self.setup_world(overwrite=False)
        self.map = self.setup_map()
        self.plot = None

    def setup_world(self, overwrite: bool=False) -> Definition:
        """ Extract ETS2/ATS archives to an intermediate cache for parsing """
        extractor = self.simulator.RootGameFolder / 'scs_extractor.exe'
        shutil.copy(self.ExtractorExecutable, extractor)

        cache_dir = self.simulator.mod_dir / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"Setting up extracted game archives cache in '{cache_dir}'...")

        for archive in ['def']:  # It looks like base.scs and others are not needed
            if (cache_dir / archive).exists() and not overwrite:
                print(f"Skipping '{self.simulator.RootGameFolder / archive}.scs' ...")
                continue
            print(f"Extracting '{self.simulator.RootGameFolder / archive}.scs' (This takes a few minutes)...")
            if platform.system() == 'Windows':
                extract_command = [str(extractor), archive + '.scs', str(cache_dir)]
            else:
                extract_command = ['wineconsole', str(extractor), archive + '.scs', str(cache_dir)]
            subprocess.check_call(extract_command, cwd=self.simulator.RootGameFolder)
        extractor.unlink()

        if (cache_dir / 'world.pkl').exists():
            with open(cache_dir / 'world.pkl', 'rb') as world_pkl:
                world = pickle.load(world_pkl)
        else:
            world = Definition(cache_dir / 'def/world', recursive=True)
            with open(cache_dir / 'world.pkl', 'wb') as world_pkl:
                pickle.dump(world, world_pkl)
        return world

    def setup_map(self) -> Map:
        """ Open and parse ETS2/ATS text map file """
        map = Map(self.simulator.mod_dir / 'map/indy500.txt')
        return map



# region Unit Tests


class TestPoliceman(unittest.TestCase):

    @unittest.skipUnless(ETS2.RootGameFolder.exists(), "ETS2 not installed")
    def test_ets2(self):
        with ETS2() as ets2:
            policeman = Policeman(ets2)


    @unittest.skipUnless(ATS.RootGameFolder.exists(), "ATS not installed")
    def test_ats(self):
        with ATS() as ats:
            policeman = Policeman(ats)


# endregion
