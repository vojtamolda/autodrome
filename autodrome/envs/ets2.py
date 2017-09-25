import gym
import unittest
import numpy as np

from ..simulator import ETS2
from .env import SimulatorEnv


class ETS2Env(SimulatorEnv):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simulator = ETS2()
        self.simulator.start()


# region Unit Tests


class TestETS2Env(unittest.TestCase):

    @unittest.skipUnless(ETS2.RootGameFolder.exists(), "ETS2 not installed")
    def test_gym(self):
        env = gym.make('ETS2-Indy500-v0')
        image = env.reset()
        for i in range(100):
            image, reward, done, info = env.step([1, 1])
        env.close()

    @unittest.skipUnless(ETS2.RootGameFolder.exists(), "ETS2 not installed")
    def test_reliability(self):
        env = gym.make('ETS2-Indy500-v0')
        for episode in range(10):
            done, pixels = False, env.reset()
            while not done:
                action = np.array([1, 2])  # Straight and Full Throttle :)
                pixels, reward, done, info = env.step(action)
        env.close()


# endregion
