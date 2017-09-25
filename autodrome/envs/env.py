import gym
import time
import numpy as np
import matplotlib.pyplot as plt

from ..simulator import Simulator


class SimulatorEnv(gym.Env):

    def __init__(self, map:str):
        super().__init__()
        self.action_space = gym.spaces.MultiDiscrete(nvec=[3, 3])  # [Left, Straight, Right], [Accelerate, Coast, Brake]
        width, height = int(Simulator.Config['r_mode_width']), int(Simulator.Config['r_mode_height'])
        self.observation_space = gym.spaces.Box(0, 255, shape=[width, height, 3], dtype=np.uint8)  # Raw Screen Pixels
        self.simulator = None
        self.figure = None
        self.image = None
        self.data = None
        self.map = map

    def step(self, action: np.ndarray) -> tuple:
        self.simulator.control(steer=action[0] - 1,  acceleration=action[1] - 1)
        pixels, self.data = self.simulator.frame(self.data)
        if (self.data.wearEngine > 0 or self.data.wearTransmission > 0
            or self.data.wearCabin > 0 or self.data.wearChassis > 0):
            reward, done = -1, True
        else:
            reward, done = +1, False
        return self.image, reward, done, {}

    def reset(self) -> np.array:
        self.simulator.command(f'preview {self.map}')
        self.data = self.simulator.wait()
        pixels, self.data = self.simulator.frame(self.data)
        if self.data.parkingBrake:
            self.simulator.keyboard.type(' ')  # Release parking brake
        self.simulator.keyboard.type('4')  # Switch to bumper camera
        self.image = self.simulator.window.capture()
        return self.image

    def render(self, mode='human'):
        if self.figure:
            self.figure = plt.figure()
        plt.imshow(self.image)
        plt.show()
        time.sleep(0.01)

    def close(self):
        if self.figure:
            self.figure.close()
        self.simulator.terminate()

