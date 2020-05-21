import sys
import shutil
import typing
from pathlib import Path

from nubia import command, argument

from scdatatools import forge


@command(help="Convert a DataForge file to a readable format")
@argument("forge_file", description="DataForge (.dcb) file to extract data from", positional=True)
@argument(
    "output",
    description="The output directory to extract files into or the output path if --single. "
                "Defaults to current directory",
    aliases=["-o"],
)
@argument(
    "file_filter",
    description="Posix style file filter of which files to extract",
    aliases=["-f"]
)
def unforge(
        forge_file: typing.Text,
        file_filter: typing.Text = "*",
        output: typing.Text = ".",
        single: bool = False,
):
    forge_file = Path(forge_file)
    output = Path(output).absolute()
    file_filter = file_filter.strip("'").strip('"')

    if not forge_file.is_file():
        sys.stderr.write(f"Could not open DataForge file {forge_file}\n")
        sys.exit(1)

    print(f"Opening DataForge file: {forge_file}")
    dcb = forge.DataCoreBinary(str(forge_file))

    if single:
        print(f"Extracting first match for filter '{file_filter}' to {output}")
        print("=" * 120)
        records = dcb.search_filename(file_filter)
        if not records:
            sys.stderr.write(f"No files found for filter")
            sys.exit(2)
        record = records[0]

        print(f"Extracting {record.filename}")

        if not output.name:
            output = output / Path(record.filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        # given an output name - use it instead of the name in the record
        with open(str(output), "wb") as target:
            target.writelines(dcb.dump_record_json(record))

    else:
        print(f"Extracting files into {output} with filter '{file_filter}'")
        print("=" * 120)
        for record in dcb.search_filename(file_filter):
            record_output = output / Path(record.filename)
            record_output.parent.mkdir(parents=True, exist_ok=True)
            print(str(record_output))
            with open(str(record_output), "w") as target:
                target.writelines(dcb.dump_record_json(record))
