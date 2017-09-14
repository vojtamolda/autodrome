import gym
import unittest

from ..simulator import ATS
from .env import SimulatorEnv


class ATSEnv(SimulatorEnv):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simulator = ATS()
        self.simulator.start()


# region Unit Tests


class TestATSEnv(unittest.TestCase):
    
    def test_gym(self):
        env = gym.make('ATS-Indy500-v0')
        image = env.reset()
        for i in range(100):
            image, reward, done, info = env.step([1, 1])
        env.close()


# end region
