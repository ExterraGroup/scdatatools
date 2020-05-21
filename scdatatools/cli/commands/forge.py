import typing

from nubia import command, argument

from scdatatools import forge


@command(help="Convert a DataForge file to a readable format")
@argument("forge_file", description="DataForge file to convert", positional=True)
def unforge(forge_file: typing.Text):
    d = forge.DataCoreBinary(forge_file)
