import gym
import argparse
import numpy as np
import autodrome.envs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run ETS2/ATS as an OpenAI gym environment")
    parser.add_argument('env', choices=['ETS2-Indy500-v0', 'ATS-Indy500-v0'], default='ATS-Indy500-v0',
                        help="OpeAI gym environment to run (i.e. ETS2-Indy500-v0, ATS-Indy500-v0)")
    parser.add_argument('--render', choices=[None, 'human', 'rgb'], default=None,
                        help="Show a windows with rendered simulation state")
    args = parser.parse_args()

    env = gym.make(args.env)
    env.reset()

    done = False
    while not done:
        action = np.array([1, 1])
        pixels, reward, done, info = env.step(action)
        if args.render:
            env.render(mode=args.render)
    env.close()
