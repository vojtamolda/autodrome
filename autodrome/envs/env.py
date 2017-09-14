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
        self.telemetry = None
        self.figure = None
        self.image = None
        self.map = map

    def step(self, action: np.ndarray) -> tuple:
        self.simulator.control(steer=action[0] - 1,  acceleration=action[1] - 1)
        pixels, self.telemetry = self.simulator.frame(self.telemetry)
        return self.image, +1, False, {}

    def reset(self) -> np.array:
        self.simulator.command(f'preview {self.map}')
        self.telemetry = self.simulator.wait()
        pixels, self.telemetry = self.simulator.frame(self.telemetry)
        if self.telemetry.parkingBrake:
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
