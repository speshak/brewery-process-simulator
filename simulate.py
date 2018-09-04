#!/usr/bin/env python3
import simpy


def run_simulation():
    env = simpy.Environment()

    env.run()


if __name__ == '__main__':
    run_simulation()
