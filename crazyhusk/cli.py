"""Expose crazyhusk functionality to the commandline."""
import argparse


def run():
    """Run the crazyhusk CLI entrypoint."""
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    print(args)
