from xml.dom import minidom
from xml.etree import ElementTree


def pprint_xml_tree(tree: ElementTree, indent: str = "    ") -> str:
    """ Pretty prints an XML ElementTree to a string """
    return minidom.parseString(ElementTree.tostring(tree.getroot())).toprettyxml(
        indent=indent
    )
