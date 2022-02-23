"""
Invokes crazyhusk CLI when the crazyhusk module is run as a script.

Example: python -m crazyhusk list_engines
"""


def main() -> None:
    # CrazyHusk
    from crazyhusk import cli

    cli.run()


if __name__ == "__main__":
    main()
