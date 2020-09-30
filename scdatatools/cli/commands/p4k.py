import sys
import shutil
import typing
from pathlib import Path

from nubia import command, argument

from scdatatools import p4k


@command(help="Extract files from a P4K file")
@argument("p4k_file", description="P4K file to unpack files from", positional=True)
@argument("single", description="Extract first matching file only", aliases=["-1"])
@argument("convert_cryxml",
          description="Automatically convert CryXMLb files to JSON (the original will also be extracted)",
          aliases=["-c"])
@argument(
    "output",
    description="The output directory to extract files into or the output path if --single. "
    "Defaults to current directory",
    aliases=["-o"],
)
@argument(
    "file_filter",
    description="Posix style file filter of which files to extract. Defaults to '*'",
    aliases=["-f"],
)
def unp4k(
    p4k_file: typing.Text,
    output: typing.Text = ".",
    file_filter: typing.Text = "*",
    convert_cryxml: bool = False,
    single: bool = False,
):
    output = Path(output).absolute()
    p4k_file = Path(p4k_file)
    file_filter = file_filter.strip("'").strip('"')

    if not p4k_file.is_file():
        sys.stderr.write(f"Could not open p4k file {p4k_file}\n")
        sys.exit(1)

    print(f"Opening p4k file: {p4k_file}")
    try:
        p = p4k.P4KFile(str(p4k_file))
    except KeyboardInterrupt:
        sys.exit(1)

    if single:
        print(f"Extracting first match for filter '{file_filter}' to {output}")
        print("=" * 80)
        found_files = p.search(file_filter)
        if not found_files:
            sys.stderr.write(f"No files found for filter")
            sys.exit(2)
        extract_file = found_files[0]

        print(f"Extracting {extract_file.filename}")

        if output.name:
            # given an output name - use it instead of the name in the P4K
            output.parent.mkdir(parents=True, exist_ok=True)
            with p.open(extract_file) as source, open(str(output), "wb") as target:
                shutil.copyfileobj(source, target)
        else:
            output.mkdir(parents=True, exist_ok=True)
            p.extract(extract_file, path=str(output), convert_cryxml=convert_cryxml)

    else:
        print(f"Extracting files into {output} with filter '{file_filter}'")
        print("=" * 80)
        output.mkdir(parents=True, exist_ok=True)
        try:
            p.extract_filter(file_filter=file_filter, path=str(output), convert_cryxml=convert_cryxml)
        except KeyboardInterrupt:
            pass
