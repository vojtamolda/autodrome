import gym
import unittest
import numpy as np

from ..simulator import ATS
from .env import SimulatorEnv


class ATSEnv(SimulatorEnv):
    
    def __init__(self, *args, **kwargs):
        kwargs['simulator'] = ATS()
        super().__init__(*args, **kwargs)


# region Unit Tests


class TestATSEnv(unittest.TestCase):

    @unittest.skipUnless(ATS.RootGameFolder.exists(), "ATS not installed")
    def test_gym(self):
        env = gym.make('ATS-Indy500-v0')
        image = env.reset()
        for step in range(100):
            action = np.array([1, 2])  # Straight and Coast
            image, reward, done, info = env.step(action)
        env.close()

    @unittest.skipUnless(ATS.RootGameFolder.exists(), "ATS not installed")
    def test_reliability(self):
        env = gym.make('ATS-Indy500-v0')
        for episode in range(10):
            done, pixels = False, env.reset()
            while not done:
                action = np.array([1, 2])  # Straight and Full Throttle :)
                pixels, reward, done, info = env.step(action)
        env.close()


# endregion
