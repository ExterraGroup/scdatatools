__all__ = ["DataCoreBinary"]

import os
import sys
import json
import mmap
import ctypes
import fnmatch
from io import IOBase
from collections import defaultdict

from scdatatools.forge import dftypes
from scdatatools.forge.utils import read_and_seek
from scdatatools.forge.dftypes.enums import DataTypes


class DataCoreBinaryMMap(mmap.mmap):
    def __new__(cls, filename_or_file, *args, **kwargs):
        if isinstance(filename_or_file, IOBase):
            _ = filename_or_file
        else:
            _ = open(filename_or_file, "rb+")
        instance = super().__new__(cls, fileno=_.fileno(), length=0, *args, **kwargs)
        instance.file = _
        return instance

    def close(self, *args, **kwargs):
        try:
            super().close(*args, **kwargs)
        finally:
            self.file.close()

    def seek(self, *args, **kwargs):
        # make this work like normal seek() where you get the offset after the seek
        super().seek(*args, **kwargs)
        return self.tell()


class DataCoreBinary:
    def __init__(self, filename_or_data):
        if isinstance(filename_or_data, str):
            self.raw_data = DataCoreBinaryMMap(filename_or_data)
        else:
            self.raw_data = filename_or_data

        self.header = read_and_seek(self, dftypes.DataCoreHeader)
        self.structure_definitions = read_and_seek(
            self, dftypes.StructureDefinition * self.header.structure_definition_count
        )
        self.property_definitions = read_and_seek(
            self, dftypes.PropertyDefinition * self.header.property_definition_count
        )
        self.enum_definitions = read_and_seek(
            self, dftypes.EnumDefinition * self.header.enum_definition_count
        )
        self.data_mapping_definitions = read_and_seek(
            self,
            dftypes.DataMappingDefinition * self.header.data_mapping_definition_count,
        )
        self.records = read_and_seek(
            self, dftypes.Record * self.header.record_definition_count
        )
        self.values = {
            DataTypes.Int8: read_and_seek(self, ctypes.c_int8 * self.header.int8_count),
            DataTypes.Int16: read_and_seek(
                self, ctypes.c_int16 * self.header.int16_count
            ),
            DataTypes.Int32: read_and_seek(
                self, ctypes.c_int32 * self.header.int32_count
            ),
            DataTypes.Int64: read_and_seek(
                self, ctypes.c_int64 * self.header.int64_count
            ),
            DataTypes.UInt8: read_and_seek(
                self, ctypes.c_uint8 * self.header.uint8_count
            ),
            DataTypes.UInt16: read_and_seek(
                self, ctypes.c_uint16 * self.header.uint16_count
            ),
            DataTypes.UInt32: read_and_seek(
                self, ctypes.c_uint32 * self.header.uint32_count
            ),
            DataTypes.UInt64: read_and_seek(
                self, ctypes.c_uint64 * self.header.uint64_count
            ),
            DataTypes.Boolean: read_and_seek(
                self, ctypes.c_bool * self.header.boolean_count
            ),
            DataTypes.Float: read_and_seek(
                self, ctypes.c_float * self.header.float_count
            ),
            DataTypes.Double: read_and_seek(
                self, ctypes.c_double * self.header.double_count
            ),
            DataTypes.GUID: read_and_seek(self, dftypes.GUID * self.header.guid_count),
            DataTypes.StringRef: read_and_seek(
                self, dftypes.StringReference * self.header.string_count
            ),
            DataTypes.Locale: read_and_seek(
                self, dftypes.LocaleReference * self.header.locale_count
            ),
            DataTypes.EnumChoice: read_and_seek(
                self, dftypes.EnumChoice * self.header.enum_count
            ),
            DataTypes.StrongPointer: read_and_seek(
                self, dftypes.StrongPointer * self.header.strong_value_count
            ),
            DataTypes.WeakPointer: read_and_seek(
                self, dftypes.WeakPointer * self.header.weak_value_count
            ),
            DataTypes.Reference: read_and_seek(
                self, dftypes.Reference * self.header.reference_count
            ),
            DataTypes.EnumOption: read_and_seek(
                self, dftypes.StringReference * self.header.enum_option_name_count
            ),
        }

        self.text = memoryview(
            self.raw_data[
                self.raw_data.tell(): self.raw_data.tell() + self.header.text_length
            ]
        )
        self.raw_data.seek(self.header.text_length, os.SEEK_CUR)

        self.structure_instances = defaultdict(list)
        for mapping in self.data_mapping_definitions:
            struct_def = self.structure_definitions[mapping.structure_index]
            struct_size = struct_def.calculated_data_size
            for i in range(mapping.structure_count):
                # self.structure_instances[mapping.structure_index].append(self.raw_data.tell())
                offset = self.raw_data.tell()
                self.structure_instances[mapping.structure_index].append(
                    dftypes.StructureInstance(
                        self,
                        memoryview(self.raw_data[offset: offset + struct_size]),
                        struct_def,
                    )
                )
                self.raw_data.seek(struct_size, os.SEEK_CUR)
        assert self.raw_data.tell() == len(self.raw_data)

        self.records_by_guid = {r.id.value: r for r in self.records}

    def string_for_offset(self, offset: int, encoding="UTF-8") -> str:
        try:
            end = self.text.obj.index(0x00, offset)
            return bytes(self.text[offset:end]).decode(encoding)
        except ValueError:
            sys.stderr.write(f"Invalid string offset: {offset}")
            return ""

    def dump_record_json(self, record, indent=4):
        def view_objs(obj):
            if (
                    isinstance(obj, dftypes.Reference)
                    and obj.value.value in self.records_by_guid
            ):
                # TODO: this probably shouldnt be here, im tired
                obj = self.records_by_guid[obj.value.value]

            if isinstance(
                    obj,
                    (
                            dftypes.StructureInstance,
                            dftypes.WeakPointer,
                            dftypes.ClassReference,
                            dftypes.Record,
                            dftypes.StrongPointer,
                    ),
            ):
                return {obj.name: obj.properties}
            elif hasattr(obj, 'value'):
                return obj.value
            else:
                return repr(obj)

        return json.dumps(record.properties, indent=indent, default=view_objs)

    def search_filename(self, file_filter, ignore_case=True):
        """ Search the records by filename """
        file_filter = "/".join(
            file_filter.split("\\")
        )  # normalize path slashes from windows to posix
        if ignore_case:
            file_filter = file_filter.lower()
            return [
                _
                for _ in self.records
                if fnmatch.fnmatch(_.filename.lower(), file_filter)
            ]
        return [_ for _ in self.records if fnmatch.fnmatchcase(_.filename, file_filter)]
