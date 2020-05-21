class AttrDict(dict):
    """
    A dict that allows access of it's keys through '.' notation. This will automatically convert any nested
    dicts into `AttrDict` instances as well so you can access nested items with dot notation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_dicts()

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        if isinstance(value, dict) and not isinstance(value, AttrDict):
            self[item] = AttrDict(value)
        else:
            self[item] = value

    def _convert_dicts(self):
        """ update all dicts within this dict to be `AttrDict` dicts recursively """
        for k in self.keys():
            if isinstance(self[k], dict):
                if not isinstance(self[k], AttrDict):
                    self[k] = AttrDict(self[k])
                self[k].__convert_dicts()
