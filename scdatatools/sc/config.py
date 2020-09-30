import csv

from scdatatools.cryxml import dict_from_cryxml_file


class Profile:
    def __init__(self, sc):
        self.sc = sc

        with self.sc.p4k.open('Data/Libs/Config/defaultProfile.xml') as f:
            self.default = dict_from_cryxml_file(f)

    def actionmap_to_dict(self, language=None):
        m = {}
        for am in self.default['profile']['actionmap']:
            label = self.sc.gettext(am['@UILabel']) if '@UILabel' in am and am['@UILabel'] else self.sc.gettext(am['@name'])
            if label not in m:
                m[label] = {}

            if 'action' not in am:
                continue

            if not isinstance(am['action'], list):
                am['action'] = [am['action']]

            for a in am['action']:
                al = self.sc.gettext(a['@UILabel']) if '@UILabel' in a and a['@UILabel'] else self.sc.gettext(a['@name'])
                m[label][al] = {
                    self.sc.gettext(k).lstrip('@'): self.sc.gettext(v) if isinstance(v, str) else v
                    for k, v in a.items() if k not in ['@name', '@UILabel']
                }
        return m

    def dump_actionmap_csv(self, fp, language=None):
        am = self.actionmap_to_dict(language)
        fieldnames = ['Category', 'Action', 'ActivationMode', 'keyboard', 'mouse',
                      'joystick', 'gamepad', 'UIDescription']
        writer = csv.DictWriter(fp, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for c, am in am.items():
            for l, a in am.items():
                writer.writerow({**{'Category': c, 'Action': l}, **a})