import ctypes
import os


def read_and_seek(dcb, data_type, buffer=None):
    """
    Reads a ctypes Structure from a `buffer`, then seeks the buffer to after the read data.

    :param dcb: The :class:`DataCoreBinary` related to this object. This will be assigned to the `_dcb` attribute on the newly
        read :class:`ctypes.Structure`
    :param data_type: A :class:`ctypes` object.
    :param buffer: The
    """
    buffer = buffer or dcb.raw_data
    r = data_type.from_buffer(buffer, buffer.tell())
    setattr(r, "_dcb", dcb)
    buffer.seek(ctypes.sizeof(r), os.SEEK_CUR)
    return r
