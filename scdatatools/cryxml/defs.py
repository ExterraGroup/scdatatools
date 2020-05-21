import ctypes
from ctypes import LittleEndianStructure, sizeof


class CryXMLBHeader(LittleEndianStructure):
    _fields_ = [
        ("signature", ctypes.c_char * 8),
        ("xml_size", ctypes.c_uint32),
        ("node_table_offset", ctypes.c_uint32),
        ("node_count", ctypes.c_uint32),
        ("attributes_table_offset", ctypes.c_uint32),
        ("attributes_count", ctypes.c_uint32),
        ("child_table_offset", ctypes.c_uint32),
        ("child_table_count", ctypes.c_uint32),
        ("string_data_offset", ctypes.c_uint32),
        ("string_data_size", ctypes.c_uint32),
    ]


class CryXMLBNodeIndex(LittleEndianStructure):
    _fields_ = [("index", ctypes.c_uint32)]


class CryXMLBNode(LittleEndianStructure):
    _fields_ = [
        ("tag_string_offset", ctypes.c_uint32),
        ("content_string_offset", ctypes.c_uint32),
        ("attribute_count", ctypes.c_uint16),
        ("child_count", ctypes.c_uint16),
        ("parent_index", ctypes.c_uint32),
        ("first_attribute_index", ctypes.c_uint32),
        ("first_child_index", ctypes.c_uint32),
        # There seems to Abe a mismatch in CIGs XMLBinary::Node and source from lumberyard.
        # There's an extra blank u_int32 at the ned of the struct for no reason? Hence the *2 below
        (
            "reserved",
            ctypes.c_char * (sizeof(ctypes.c_uint32) * 2 - sizeof(CryXMLBNodeIndex)),
        ),
    ]


class CryXMLBAttribute(LittleEndianStructure):
    _fields_ = [
        ("key_string_offset", ctypes.c_uint32),
        ("value_string_offset", ctypes.c_uint32),
    ]


CRYXML_NO_PARENT = 0xFFFFFFFF
