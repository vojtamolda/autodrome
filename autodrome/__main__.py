import argparse
from .simulator import ETS2, ATS


Simulators = {'ETS2': ETS2, 'ATS': ATS}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ETS2/ATS as a Self-Driving Car Simulator")
    parser.add_argument('simulator', choices=Simulators,
                        help="Game to run (i.e. ETS2 or ATS)")
    parser.add_argument('-m', '--map', default=None,
                        help="Map to drive on (i.e. 'europe' for ETS2 or 'usa' for ATS)")
    args = parser.parse_args()

    with Simulators[args.simulator]() as simulator:
        if args.map is not None:
            simulator.command('preview {}'.format(args.map))
        while simulator.process.poll() is None:
            reply = simulator.telemetry.receive()
