import gym
import unittest

from ..simulator import ETS2
from .env import SimulatorEnv


class ETS2Env(SimulatorEnv):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simulator = ETS2()
        self.simulator.start()


# region Unit Tests


class TestETS2Env(unittest.TestCase):

    def test_gym(self):
        env = gym.make('ETS2-Indy500-v0')
        image = env.reset()
        for i in range(100):
            image, reward, done, info = env.step([1, 1])
        env.close()


# end region
