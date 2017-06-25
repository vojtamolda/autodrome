import unittest
import matplotlib.pyplot as plt

from simulator import SimulatorABC, ATS, ETS2

from .map import Map
from .definition import Definition


class Policeman:
    def __init__(self, simulator: SimulatorABC):
        self.map = Map(simulator.UserGameFolder / 'mod/map/indy500.txt/')
        self.world = Definition(simulator.RootGameFolder / 'def/world', recursive=True)

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
