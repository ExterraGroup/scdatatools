__all__ = ["DataTypes", "ConversionTypes", "StringSize"]

from enum import IntEnum


class DataTypes(IntEnum):
    Reference = 0x0310
    WeakPointer = 0x0210
    StrongPointer = 0x0110
    Class = 0x0010
    EnumChoice = 0x000F
    GUID = 0x000E
    Locale = 0x000D
    Double = 0x000C
    Float = 0x000B
    StringRef = 0x000A
    UInt64 = 0x0009
    UInt32 = 0x0008
    UInt16 = 0x0007
    UInt8 = 0x0006
    Int64 = 0x0005
    Int32 = 0x0004
    Int16 = 0x0003
    Int8 = 0x0002
    Boolean = 0x0001
    EnumValueName = 0xBEEF0  # TODO: made this up cause it didnt exist
    ArrayPointer = 0xBEEF1  # TODO: added for scdatatools


class ConversionTypes(IntEnum):
    Attribute = 0
    ComplexArray = 1
    SimpleArray = 2
    ClassArray = 3


class StringSize(IntEnum):
    Int8 = 1
    Int16 = 2
    Int32 = 4
