import csv

from scdatatools.cryxml import etree_from_cryxml_file
from scdatatools.utils import etree_to_dict


class Profile:
    def __init__(self, sc, p4k_path):
        self.sc = sc

        with self.sc.p4k.open(p4k_path) as f:
            self.xml = etree_from_cryxml_file(f)
            self.json = etree_to_dict(self.xml)

    def actionmap(self, language=None):
        m = {}
        for am in self.json['profile']['actionmap']:
            category = self.sc.gettext(am['@UICategory'], language=language) if '@UICategory' in am else 'Other'

            if '@UILabel' in am and am['@UILabel']:
                label = self.sc.gettext(am['@UILabel'], language=language)
            else:
                label = self.sc.gettext(am['@name'], language=language)

            if category not in m:
                m[category] = {}

            if label not in m[category]:
                m[category][label] = {}

            if 'action' not in am:
                continue

            if not isinstance(am['action'], list):
                am['action'] = [am['action']]

            for a in am['action']:
                al = self.sc.gettext(a['@UILabel'], language=language) \
                    if '@UILabel' in a and a['@UILabel'] else self.sc.gettext(a['@name'], language=language)
                m[category][label][al] = {
                    self.sc.gettext(k, language=language).lstrip('@'):
                        self.sc.gettext(v, language=language) if isinstance(v, str) else v
                    for k, v in a.items() if k not in ['@name', '@UILabel']
                }
        return m

    def dump_actionmap_csv(self, fp, language=None):
        am = self.actionmap(language)
        fieldnames = ['Category', 'Action', 'ActivationMode', 'keyboard', 'mouse',
                      'joystick', 'gamepad', 'UIDescription']
        writer = csv.DictWriter(fp, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for ui_category, action_category in am.items():
            for category, actions in action_category.items():
                for label, action in actions.items():
                    writer.writerow({**{'Category': category, 'Action': label}, **action})
