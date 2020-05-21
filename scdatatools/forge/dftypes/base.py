import struct


class BaseType:
    _struct_format = ""
    fields = []
    references = {}
    # __slots__ = ['forge', 'offset']

    def __init__(self, forge, data, offset=None):
        self.forge = forge
        self.offset = offset
        if data is not None:
            for i, _ in enumerate(struct.unpack(self._struct_format, data)):
                setattr(self, self.fields[i], _)
        else:
            for field in self.fields:
                setattr(self, field, None)

    def __getattr__(self, item):
        ref = self.references[item]
        if len(ref) == 3:
            forge_attr, lookup_local_ref, lookup_attr = ref
            return getattr(
                getattr(self.forge, forge_attr)[getattr(self, lookup_local_ref)],
                lookup_attr,
            )
        elif len(ref) == 2:
            forge_attr, lookup_ref = ref
            return getattr(self.forge, forge_attr)[getattr(self, lookup_ref)]

    @classmethod
    def from_file(cls, forge_file):
        offset = forge_file.tell()
        return cls(forge_file, forge_file.read(cls.size()), offset)

    @classmethod
    def size(cls):
        """ Number of Bytes of this definition """
        return struct.Struct(cls._struct_format).size

    @property
    def calculated_data_size(self):
        """ Size of the data represented by this definition """
        return self.size()


class SimpleBaseType(BaseType):
    fields = ["value"]
    # __slots__ = BaseType.# __slots__ + fields


class LookupBaseType(BaseType):
    fields = ["offset"]
    forge_ref = "string_map"
    # __slots__ = BaseType.# __slots__ + fields

    def __getattr__(self, item):
        try:
            return getattr(self.forge, self.forge_ref)[self.offset]
        except KeyError:
            return f"offset not found [{self.offset}]"
