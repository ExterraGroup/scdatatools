import csv
from xml.etree import ElementTree as ET

from .utils import etree_to_dict


def profile_to_dict(filename):
    return etree_to_dict(ET.parse(filename))


def profile_actionmaps_to_csv(filename_or_dict, out_filename):
    pf_dict = profile_to_dict(filename_or_dict) if isinstance(filename_or_dict, str) else filename_or_dict
    columns = set()
    mappings = []
    for am in pf_dict['profile']['actionmap']:
        def _process_action(action):
            _ = {'category': am.get('@UICategory', ''), 'label': am.get('@UILabel', ''), 'action': action['@name']}
            _.update(**{k.lstrip('@'): v for k, v in action.items()})
            columns.update([_.lstrip('@') for _ in action.keys()])
            mappings.append(_)

        if not isinstance(am['action'], list):
            _process_action(am['action'])
        else:
            for action in am['action']:
                _process_action(action)
    fieldnames = ['category', 'label', 'action'] + sorted(list(columns))
    with open(out_filename, 'w') as csvfile:
        c = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore')
        c.writeheader()
        c.writerows(mappings)
