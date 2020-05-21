import enum
import struct
import ctypes
from functools import cached_property
from ctypes import LittleEndianStructure

from .enums import *
from .utils import AttrDict


DCB_NO_PARENT = 0xFFFFFFFF


class DataCoreBase(LittleEndianStructure):
    @property
    def dcb(self):
        return getattr(self, "_dcb", getattr(self._b_base_, "_dcb", None))


class DataCoreNamed(DataCoreBase):
    @cached_property
    def name(self):
        return self.dcb.string_for_offset(self.name_offset)


class DataCoreHeader(DataCoreBase):
    _fields_ = [
        ("unknown0", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("unknown1", ctypes.c_uint16),
        ("unknown2", ctypes.c_uint16),
        ("unknown3", ctypes.c_uint16),
        ("unknown4", ctypes.c_uint16),
        ("structure_definition_count", ctypes.c_uint32),
        ("property_definition_count", ctypes.c_uint32),
        ("enum_definition_count", ctypes.c_uint32),
        ("data_mapping_definition_count", ctypes.c_uint32),
        ("record_definition_count", ctypes.c_uint32),
        ("boolean_count", ctypes.c_uint32),
        ("int8_count", ctypes.c_uint32),
        ("int16_count", ctypes.c_uint32),
        ("int32_count", ctypes.c_uint32),
        ("int64_count", ctypes.c_uint32),
        ("uint8_count", ctypes.c_uint32),
        ("uint16_count", ctypes.c_uint32),
        ("uint32_count", ctypes.c_uint32),
        ("uint64_count", ctypes.c_uint32),
        ("float_count", ctypes.c_uint32),
        ("double_count", ctypes.c_uint32),
        ("guid_count", ctypes.c_uint32),
        ("string_count", ctypes.c_uint32),
        ("locale_count", ctypes.c_uint32),
        ("enum_count", ctypes.c_uint32),
        ("strong_value_count", ctypes.c_uint32),
        ("weak_value_count", ctypes.c_uint32),
        ("reference_count", ctypes.c_uint32),
        ("enum_option_name_count", ctypes.c_uint32),
        ("text_length", ctypes.c_uint32),
        ("unknown6", ctypes.c_uint32),
    ]


class StructureDefinition(DataCoreNamed):
    _fields_ = [
        ("name_offset", ctypes.c_uint32),
        ("parent_index", ctypes.c_uint32),
        ("property_count", ctypes.c_uint16),
        ("first_property_index", ctypes.c_uint16),
        ("node_type", ctypes.c_uint32),
    ]

    def __repr__(self):
        return (
            f'<Struct {self.name} parent:{"None" if self.parent is None else self.parent.name} '
            f"props:{self.property_count} type:{self.node_type}>"
        )

    @property
    def parent(self):
        return (
            None
            if self.parent_index == DCB_NO_PARENT
            else self.dcb.structure_definitions[self.parent_index]
        )

    @cached_property
    def properties(self):
        if not hasattr(self, "_props"):
            props = [
                self.dcb.property_definitions[_]
                for _ in range(
                    self.first_property_index,
                    self.first_property_index + self.property_count,
                )
            ]
            if self.parent_index != 0xFFFFFFFF:
                props = (
                    self.dcb.structure_definitions[self.parent_index].properties + props
                )
            setattr(self, "_props", props)
        return getattr(self, "_props", [])

    @cached_property
    def calculated_data_size(self):
        size = 0
        for prop in self.properties:
            if prop.conversion_type != ConversionTypes.Attribute:
                size += ctypes.sizeof(DATA_TYPE_LOOKUP[DataTypes.ArrayPointer])
            else:
                size += prop.calculated_data_size
        return size


class PropertyDefinition(DataCoreNamed):
    _fields_ = [
        ("name_offset", ctypes.c_uint32),
        ("structure_index", ctypes.c_uint16),
        ("data_type", ctypes.c_uint16),
        ("conversion_type", ctypes.c_uint16),
        ("padding", ctypes.c_uint16),
    ]

    def __repr__(self):
        return (
            f"<PropertyDef {self.name} struct:{self.dcb.structure_definitions[self.structure_index].name} "
            f"type:{DataTypes(self.data_type).name} conv:{ConversionTypes(self.conversion_type).name}>"
        )

    @cached_property
    def calculated_data_size(self):
        if self.data_type == DataTypes.Class:
            return self.type_def.calculated_data_size
        return ctypes.sizeof(self.type_def)

    @cached_property
    def type_def(self):
        if self.data_type in DATA_TYPE_LOOKUP:
            return DATA_TYPE_LOOKUP[self.data_type]
        elif self.data_type == DataTypes.Class:
            return self.dcb.structure_definitions[self.structure_index]
        raise TypeError(f"data_type not implemented: {self.data_type}")


class EnumDefinition(DataCoreNamed):
    _fields_ = [
        ("name_offset", ctypes.c_uint32),
        ("value_count", ctypes.c_uint16),
        ("first_value_index", ctypes.c_uint16),
    ]

    @cached_property
    def enum(self):
        return enum.Enum(
            self.name,
            [
                self.dcb.values[DataTypes.EnumOption][_].value
                for _ in range(
                    self.first_value_index, self.first_value_index + self.value_count
                )
            ],
        )


class EnumChoice(DataCoreBase):
    _fields_ = [("enum_choice_index", ctypes.c_uint32)]

    @property
    def enum(self):
        return self._enum_definition.enum

    @property
    def value(self):
        return getattr(self.enum, self.dcb.string_for_offset(self.enum_choice_index))


class DataMappingDefinition(DataCoreBase):
    _fields_ = [
        ("structure_count", ctypes.c_uint16),
        ("structure_index", ctypes.c_uint16),
    ]

    def __repr__(self):
        return (
            f"<DataMap structure:{self.structure_index} count:{self.structure_count}>"
        )


class GUID(DataCoreBase):
    _fields_ = [("raw_guid", ctypes.c_byte * 16)]

    @cached_property
    def value(self):
        c, b, a, k, j, i, h, g, f, e, d = struct.unpack("<HHI8B", self.raw_guid)
        return f"{a:08x}-{b:04x}-{c:04x}-{d:02x}{e:02x}-{f:02x}{g:02x}{h:02x}{i:02x}{j:02x}{k:02x}"

    def __repr__(self):
        return f"<GUID: {self.value}>"


class StructureInstance:
    def __init__(self, dcb=None, raw_data=None, structure_definition=None):
        self.dcb = dcb
        self.raw_data = raw_data
        self.structure_definition = structure_definition

    def read_property(self, offset: int, property_definition: PropertyDefinition):
        conv_type = property_definition.conversion_type
        data_type = property_definition.data_type

        def _clean_class_reference(cls_ref):
            cls_ref._dcb = self.dcb
            cls_ref = None if cls_ref.reference is None else cls_ref
            return cls_ref

        if conv_type == ConversionTypes.Attribute:
            if data_type in [DataTypes.StrongPointer, DataTypes.WeakPointer]:
                end_offset = offset + ctypes.sizeof(ClassReference)
                return (
                    _clean_class_reference(
                        ClassReference.from_buffer(
                            bytearray(self.raw_data[offset:end_offset])
                        )
                    ),
                    end_offset,
                )
            elif data_type == DataTypes.Class:
                end_offset = offset + property_definition.type_def.calculated_data_size
                return (
                    StructureInstance(
                        self.dcb,
                        memoryview(self.raw_data[offset:end_offset]),
                        property_definition.type_def,
                    ),
                    end_offset,
                )

            end_offset = offset + property_definition.calculated_data_size
            buf = bytearray(self.raw_data[offset:end_offset])
            prop = property_definition.type_def.from_buffer(buf)
            prop._dcb = self.dcb

            if data_type == DataTypes.EnumChoice:
                prop._enum_definition = self.dcb.enum_definitions[
                    property_definition.structure_index
                ]

            return prop.value, end_offset
        elif conv_type in [_.value for _ in ConversionTypes]:
            end_offset = offset + 8
            buf = bytearray(
                self.raw_data[offset:end_offset]
            )  # 8 == sizeof(int32 + int32)
            count, first_index = (ctypes.c_uint32 * 2).from_buffer(buf)
            if data_type == DataTypes.Class:
                clss = []
                for _ in range(count):
                    clss.append(
                        _clean_class_reference(
                            ClassReference(
                                structure_index=property_definition.structure_index,
                                instance_index=first_index + _,
                            )
                        )
                    )
                return clss, end_offset
            elif data_type in self.dcb.values:
                return (
                    [
                        self.dcb.values[property_definition.data_type][first_index + _]
                        for _ in range(count)
                    ],
                    end_offset,
                )
        raise NotImplementedError(
            f"Property has not been implemented: {property_definition}"
        )

    @property
    def name(self):
        return self.structure_definition.name

    @cached_property
    def properties(self):
        props = AttrDict()
        offset = 0
        for prop_def in self.structure_definition.properties:
            props[prop_def.name], offset = self.read_property(offset, prop_def)
        return props


class StringReference(DataCoreBase):
    _fields_ = [("string_offset", ctypes.c_uint32)]

    @cached_property
    def value(self):
        return self.dcb.string_for_offset(self.string_offset)

    def __repr__(self):
        return self.value


class LocaleReference(StringReference):
    pass


class _Pointer:
    @property
    def properties(self):
        if self.reference is not None:
            return self.reference.properties
        return {}

    @property
    def name(self):
        if self.reference is not None:
            return self.reference.name
        return ""

    @property
    def reference(self):
        if (
            self.structure_index == DCB_NO_PARENT
            or self.instance_index == DCB_NO_PARENT
        ):
            return None
        return self.dcb.structure_instances[self.structure_index][self.instance_index]

    @property
    def structure_definition(self):
        return self.dcb.structure_definitions[self.structure_index]


class StrongPointer(_Pointer, DataCoreBase):
    _fields_ = [
        ("structure_index", ctypes.c_uint32),
        ("instance_index", ctypes.c_uint32),
    ]

    def __repr__(self):
        return f"<StrongPointer structure:{self.structure_definition.name} instance:{self.instance_index}>"


class ClassReference(_Pointer, DataCoreBase):
    _fields_ = [
        ("structure_index", ctypes.c_uint32),
        ("instance_index", ctypes.c_uint32),
    ]

    def __repr__(self):
        return f"<ClassReference structure:{self.structure_definition.name} instance:{self.instance_index}>"


class WeakPointer(_Pointer, DataCoreBase):
    _fields_ = [
        ("structure_index", ctypes.c_uint32),
        ("instance_index", ctypes.c_uint32),
    ]

    def __repr__(self):
        return f"<WeakPointer structure:{self.structure_definition.name} instance:{self.instance_index}>"

    @property
    def properties(self):
        if self.reference is not None:
            return AttrDict(
                {
                    "name": self.reference.name,
                    "structure_index": self.structure_index,
                    "index": self.instance_index,
                }
            )
        return {}


class Record(_Pointer, DataCoreNamed):
    _fields_ = [
        ("name_offset", ctypes.c_uint32),
        ("filename_offset", ctypes.c_uint32),
        ("structure_index", ctypes.c_uint32),
        ("id", GUID),
        ("instance_index", ctypes.c_uint16),
        ("other_index", ctypes.c_uint16),
    ]

    @cached_property
    def name(self):
        return self.dcb.string_for_offset(self.name_offset).replace(
            f"{self.type}.", "", 1
        )

    @property
    def type(self):
        return self.reference.name

    @property
    def filename(self):
        return self.dcb.string_for_offset(self.filename_offset)

    def __repr__(self):
        return (
            f"<Record name:{self.name} {self.id.value} struct:{self.structure_definition.name} "
            f"instance:{self.instance_index}>"
        )


class Reference(DataCoreBase):
    _fields_ = [("instance_index", ctypes.c_uint32), ("value", GUID)]

    def __repr__(self):
        return f"<Reference record:{self.value.value} instance:{self.instance_index}>"


DATA_TYPE_LOOKUP = {
    DataTypes.Reference: Reference,
    DataTypes.WeakPointer: WeakPointer,
    DataTypes.StrongPointer: StrongPointer,
    # DataTypes.Class: ,
    DataTypes.EnumChoice: EnumChoice,
    DataTypes.EnumOption: StringReference,
    DataTypes.GUID: GUID,
    DataTypes.Locale: LocaleReference,
    DataTypes.Double: ctypes.c_double,
    DataTypes.Float: ctypes.c_float,
    DataTypes.StringRef: StringReference,
    DataTypes.UInt64: ctypes.c_uint64,
    DataTypes.UInt32: ctypes.c_uint32,
    DataTypes.UInt16: ctypes.c_uint16,
    DataTypes.UInt8: ctypes.c_uint8,
    DataTypes.Int64: ctypes.c_int64,
    DataTypes.Int32: ctypes.c_int32,
    DataTypes.Int16: ctypes.c_int16,
    DataTypes.Int8: ctypes.c_int8,
    DataTypes.Boolean: ctypes.c_bool,
    DataTypes.ArrayPointer: ctypes.c_int32 * 2,
}
