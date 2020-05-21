import sys

from nubia import Nubia, Options

from . import commands


def main():
    shell = Nubia(
        name="scdt", command_pkgs=commands, options=Options(persistent_history=False),
    )
    sys.exit(shell.run())
