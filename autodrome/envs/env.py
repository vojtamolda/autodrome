import gym
import math
import numpy as np

from ..simulator import Simulator
from ..policeman import Policeman


class SimulatorEnv(gym.Env):

    def __init__(self, simulator: Simulator, map: str):
        super().__init__()
        self.action_space = gym.spaces.MultiDiscrete(nvec=[3, 3])  # [Left, Straight, Right], [Accelerate, Coast, Brake]
        width, height = int(Simulator.Config['r_mode_width']), int(Simulator.Config['r_mode_height'])
        self.observation_space = gym.spaces.Box(0, 255, shape=[width, height, 3], dtype=np.uint8)  # Raw Screen Pixels

        self.map = map
        self.simulator = simulator
        self.simulator.start()

        self.policeman = Policeman(simulator)
        self.info = {'map': self.policeman.map, 'world': self.policeman.world}
        self.pixels, self.data = None, None
        self.viewer = None

    def step(self, action: np.ndarray) -> tuple:
        self.simulator.control(steer=action[0] - 1,  acceleration=action[1] - 1)
        self.pixels, self.data = self.simulator.frame(self.data)
        if self.data.wearCabin > 0 or self.data.wearChassis > 0:
            reward, done = -1, True
        else:
            reward, done = +1, False
        return self.pixels, reward, done, self.info

    def reset(self) -> np.array:
        self.simulator.command(f'preview {self.map}')
        self.data = self.simulator.wait()
        self.pixels, self.data = self.simulator.frame(self.data)
        if self.data.parkingBrake:
            self.simulator.keyboard.type(' ')  # Release parking brake
        self.simulator.keyboard.type('4')  # Switch to bumper camera
        return self.pixels

    def render(self, mode='human'):
        if mode == 'human':
            self._render_human()
        if mode == 'rgb':
            self._render_rgb()

    def _render_human(self):
        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(600, 600)
            self.viewer.set_bounds(-220, +220, -220, +220)

            truck = rendering.make_capsule(8, 4)
            truck.set_color(0.0, 0.0, 0.0)
            self.truck_transform = rendering.Transform()
            truck.add_attr(self.truck_transform)
            self.viewer.add_geom(truck)

            for node in self.policeman.map['nodes'].values():
                circle = rendering.make_circle(2)
                circle.set_color(0.6, 0.6, 0.6)
                dot_transform = rendering.Transform((node['position']['x'], -node['position']['z']))
                circle.add_attr(dot_transform)
                self.viewer.add_geom(circle)

        position, orientation = self.data.worldPlacement.position, self.data.worldPlacement.orientation
        self.truck_transform.set_rotation(orientation.heading * math.pi * 2 - math.pi / 2)
        self.truck_transform.set_translation(position.x, -position.z)
        return self.viewer.render()

    def _render_rgb(self):
        if self.viewer is None:
            from pyglet import window
            from gym.envs.classic_control import rendering
            self.viewer = rendering.SimpleImageViewer()
            width, height = self.observation_space.shape[0] // 2, self.observation_space.shape[1] // 2
            self.viewer.window = window.Window(width, height, vsync=False, resizeable=False)
            self.viewer.window.set_location(2 * width, height)

        if self.pixels is not None:
            self.viewer.imshow(self.pixels[::2, ::2, [2, 1, 0]])
            self.pixels = None
        return self.viewer.isopen

    def close(self):
        self.simulator.terminate()
