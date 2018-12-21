
# Autodrome

_Autodrome_ is a framework and [OpenAI gym](https://gym.openai.com/) environment for development of self-driving vehicles. It's built around the engine, map editor and assets of  [Euro Truck Simulator 2](https://eurotrucksimulator2.com) (ETS2) or [American Truck Simulator](https://americantrucksimulator.com) (ATS).



## Development and Testing Autonomous Vehicles in Simulation

Developing algorithms for self-driving vehicles is not an easy task. Initial excitement about behavioral cloning agents built in an afternoon quickly wears off once it's clear how hard are the corner cases where it doesn't wok. The difficult part is improving the reliability from the afternoon project level of 90% to the near-human level of 99.9999%.

Reaching this level of reliability requires a lot of infrastructure, large datasets and a flexibility to quickly run unit tests and benchmark the performance against a baseline. This is true even for a limited geo-fenced use cases like driving on highways. Goal of the project is to get the basics version of these features running by gluing together pieces that are already available elsewhere. Basic design blocks and key components are shown on the following diagram.

![Concept](https://github.com/vojtamolda/autodrome/wiki/Home/Concept.png)

There's more details about the concept of the project on the [Architecture wiki page](https://github.com/vojtamolda/autodrome/wiki/Architecture/).



## Rapid Building of Realistic Maps 

ETS2 and ATS come with a detailed and very rich 3D world environment with virtually any type of landscape. The world can be rendered in a palette of diverse lighting and weather conditions. _Autodrome_ takes advantage of this and one can test the vehicle in large number of visually distinct city, semi-urban, country or industrial environment. ETS2/ATS world map contains almost entire Europe or a large portion of the western USA scaled to 1:20.

![Editor Demo](https://github.com/vojtamolda/autodrome/wiki/Maps-and-Editor/Editor-Demo.gif)

Under the hood _Autodrone_ is actually a specialized game mod and a telemetry plugin. This means that one can take advantage of the built-in map editor and repurpose pieces of the editable map world map as scenarios for the self-driving agent. The map editor is very easy to learn and thanks to the sparse representation of the data one can easily adapt sections for his own specific needs. Extensibility of both simulators provided a great foundation thanks to large documentation and tutorials created by the modding community.

See the [Editor and Maps wiki page](https://github.com/vojtamolda/autodrome/wiki/Maps-and-Editor/) for more details and a guide how to get started with map editing.



## Reinforcement Learning

_Autodrome_ provides a Python API that can be used for a wide variety of purposes for example - data collection, behavioral cloning or reinforcement learning. The API makes it easy to use _Autodrome_ with any machine learning toolchain. One possible way to train an agent capable of driving a vehicle is deep reinforcement learning.

The project exposes a simple RL environment that implements the de-facto standard in RL research - OpenAI Gym API. The agent controls the truck and is rewarded for the travelled distance. Once the truck collides with anything the episode terminates.

![Open AI Gym Demo](https://github.com/vojtamolda/autodrome/wiki/OpenAI-Gym/Gym-Demo.gif)

There's been a significant effort invested into a flexible messaging that allows multiple instances of the simulator executed on different machines in order the feed the data hungry RL algorithms. There are more details on the topic on the [Open AI Gym wiki page](https://github.com/vojtamolda/autodrome/wiki/OpenAI-Gym/).



## Documentation & Getting Started

Check out the [Home wiki page](https://github.com/vojtamolda/autodrome/wiki/Home) to browse the project documentation and to get started. If you're impatient you can run the following commands to install all the pre-requisites.

```bash
brew install cmake zeromq capnp
pip install -r requirements.txt -r requirements-darwin.txt
```

Once you're done with the installation you can run the following snippey of Python code. It runs a single Open AI Gym episode that ends when the truck crashes into the railing on the side of the road. The agent driving the truck is a suicidal maniac that steps on the throttle and doesn't bother steering :)

```python
import gym
import numpy as np
import autodrome.envs

env = gym.make('ETS2-Indy500-v0')  # or 'ATS-Indy500-v0'
done, state = False, env.reset()
while not done:  # Episode ends when the truck crashes
    action = np.array([1, 2])  # Straight and Full Throttle :)
    state, reward, done, info = env.step(action)
    env.render()  # Display map of the world and truck position
```



## Similar Projects and Companies

Here's a list of projects and companies that have emerged since I started working on _Autodrome_ that have similar functionality:

- [AirSim](https://github.com/Microsoft/AirSim)
- [Carla](https://github.com/carla-simulator/carla)
- [DeepDrive](https://github.com/deepdrive/deepdrive)
- [Europilot](https://github.com/marsauto/europilot)
- [Waymo](https://waymo.com/tech/)
- [Applied Intuition](https://www.appliedintuition.com)
- [Zoox](https://zoox.com)
