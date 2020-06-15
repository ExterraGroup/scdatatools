import csv
from xml.etree import ElementTree as ET

from .utils import etree_to_dict


def actionmap_to_dict(filename):
    return etree_to_dict(ET.parse(filename))


def actionmap_to_csv(filename_or_dict, out_filename):
    am_dict = actionmap_to_dict(filename_or_dict) if isinstance(filename_or_dict, str) else filename_or_dict
    columns = set()
    mappings = []
    for am in am_dict['ActionMaps']['actionmap']:
        for action in am['action']:
            _ = {'group': am['@name'], 'action': action['@name']}
            for rebind in action['rebind']:
                columns.add(rebind['@device'])
                _[rebind['@device']] = f"{rebind.get('@ActivationMode', '').strip()}:{rebind.get('@input', '').strip()}"
            mappings.append(_)
    fieldnames = ['group', 'action'] + list(columns)
    with open(out_filename, 'w') as csvfile:
        c = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore')
        c.writeheader()
        c.writerows(mappings)

