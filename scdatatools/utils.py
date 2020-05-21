from collections import defaultdict
from xml.etree import ElementTree


# etree<->dict conversions from
# from https://stackoverflow.com/a/10076823


def etree_to_dict(t: ElementTree.ElementTree) -> dict:
    """ Convert the given ElementTree `t` to an dict following the following XML to JSON specification:
    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    """
    if isinstance(t, ElementTree.ElementTree):
        t = t.getroot()

    d = {t.tag: {} if hasattr(t, "attrib") else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]["#text"] = text
        else:
            d[t.tag] = text
    return d


def dict_to_etree(d: dict) -> ElementTree:
    """ Convert the given dict `d` to an ElementTree following the following XML to JSON specification:
    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    """

    def _to_etree(d, root):
        if not d:
            pass
        elif isinstance(d, str):
            root.text = d
        elif isinstance(d, dict):
            for k, v in d.items():
                assert isinstance(k, str)
                if k.startswith("#"):
                    assert k == "#text" and isinstance(v, str)
                    root.text = v
                elif k.startswith("@"):
                    assert isinstance(v, str)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ElementTree.SubElement(root, k))
                else:
                    _to_etree(v, ElementTree.SubElement(root, k))
        else:
            assert d == "invalid type", (type(d), d)

    assert isinstance(d, dict) and len(d) == 1
    tag, body = next(iter(d.items()))
    node = ElementTree.Element(tag)
    _to_etree(body, node)
    return node
