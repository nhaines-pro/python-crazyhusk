"""
Invokes crazyhusk CLI when the crazyhusk module is run as a script.

Example: python -m crazyhusk list_engines
"""

if __name__ == "__main__":
    from crazyhusk import cli

    cli.run()
