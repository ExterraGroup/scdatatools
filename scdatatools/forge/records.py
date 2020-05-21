__all__ = ["Record"]


class Record:
    """ A `Record` is a Python object representation of a `RecordDefinition` from a `DataForge` file. """

    def __init__(self, forge_file, definition, preload=False):
        """
        Create a `Record` from the given `DataForge` file, `forge_file` using the given `RecordDefinition`, `definition`

        A `Record`'s attributes are dynamically generated based on the `definition` and are lazy-loaded unless `preload`
        is `True`.

        :param preload: If true, the `Record` will read all related data from `forge_file` immediately.
        """
        self.forge_file = forge_file
        self.definition = definition

        if preload:
            # TODO: pre-load all the data from the file
            pass
