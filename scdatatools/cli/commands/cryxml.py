import json
import typing

from nubia import command, argument

from scdatatools.cryxml import etree_from_cryxml_file, dict_from_cryxml_file
from scdatatools.cryxml.utils import pprint_xml_tree


@command(help="Convert a CryXML file to xml")
@argument("cryxml_file", description="CryXML to convert", positional=True)
@argument(
    "output",
    description="Output filename or '-' for stdout. Defaults to '-'",
    aliases=["-o"],
)
def cryxml_to_xml(cryxml_file: typing.Text, output="-"):
    tree = etree_from_cryxml_file(cryxml_file)
    if output == "-":
        print(pprint_xml_tree(tree))
    else:
        with open(output, "w") as f:
            f.write(pprint_xml_tree(tree))


@command(help="Convert a CryXML file to JSON")
@argument("cryxml_file", description="CryXML to convert", positional=True)
@argument(
    "output",
    description="Output filename or '-' for stdout. Defaults to '-'",
    aliases=["-o"],
)
def cryxml_to_json(cryxml_file: typing.Text, output="-"):
    data = dict_from_cryxml_file(cryxml_file)
    if output == "-":
        print(json.dumps(data, indent=4))
    else:
        with open(output, "w") as f:
            json.dump(data, f, indent=4)
