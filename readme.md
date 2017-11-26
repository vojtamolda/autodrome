
# Autodrome

Autodrome is a toolbox for development of self-driving vehicles built around the engine, map editor and assets of [__Euro Truck Simulator 2__](https://eurotrucksimulator2.com) and [__American Truck Simulator__](https://americantrucksimulator.com).



Check out the [wiki](https://github.com/vojtamolda/autodrome/wiki) to find out more.


## Introduction

```python
import gym
from autodrome import ATS, ETS2

with ETS2() as simulator:
    simulator.process.wait()

env = gym.make('ATS-Indy500-v0')
done, state = False, env.reset()
while not done:
    state, reward, done, info = env.step()
    env.render()
```


## Installation


```bash
brew install cmake zeromq capnp
pip install -r requirements.txt -r requirements-darwin.txt

mkdir "simulator/plugin/build" && cd "simulator/plugin/build"
cmake .. && make && make install
```


## Getting Started

TODO


## Motivation

Making a behavioral cloning agent that can drive a car around a circuit can be done in an afternoon. The difficult part is taking the reliability of the algorithm from 99% to 99.99999%. The goal of this project is to provide a basic framework for developing reliable virtual unit tests.

- Machine learning is for the most part an empirical science. Quick iteration and experimentation are crucial for the development

- At the same time one wants to make sure the the latest idea won't break the behavior of the system in cases where it worked before.

## Other Projects
- [AirSim](https://github.com/Microsoft/AirSim)
- [Carla](https://github.com/carla-simulator/carla)
- [DeepDrive](https://github.com/deepdrive/deepdrive)
- [Europilot](https://github.com/marsauto/europilot)
- [Waymo](https://waymo.com/tech/)
- [Applied Intuition](https://www.appliedintuition.com)
- [Zoox](https://zoox.com)
