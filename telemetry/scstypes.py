"""Definition of Python counterparts to C data structures used by the game telemetry plugin for ETS2/ATS"""

import struct
import ctypes


class Structure(ctypes.Structure):
    """Extension of `ctypes.Structure` that can unpack itself from byte arrays"""

    def __init__(self, buffer: bytes):
        """Create a new instance and initialize all field values by unpacking the provided `bytes`"""
        if isinstance(buffer, bytes):
            unpacked_values = struct.unpack(self._type_, buffer)
            field_values = iter(unpacked_values)
        else:
            field_values = buffer

        for (field_name, field_type) in self._fields_:
            if issubclass(field_type, Structure):
                substructure = field_type(buffer=field_values)
                setattr(self, field_name, substructure)
            else:
                primitive = field_type(next(field_values))
                setattr(self, field_name, primitive)

    def __repr__(self):
        """Human readable representation for debugging, similar to `dict` """
        strings = []
        for (field_name, field_type) in self._fields_:
            field_str = str(getattr(self, field_name, None))
            strings.append("'{}': {}".format(field_name, field_str))
        return "{" + ", ".join(strings) + "}"


#  Python counterparts to primitive C types
u32_t = ctypes.c_uint32  # `scs_u32_t`
float_t = ctypes.c_float  # `scs_float_t`
double_t = ctypes.c_double  # `scs_double_t`
timestamp_t = ctypes.c_uint64  # `scs_timestamp_t`


class fvector_t(Structure):
    """Python counterpart of `scs_fvector_value_t` structure"""
    _fields_ = [('x', float_t),
                ('y', float_t),
                ('z', float_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class dvector_t(Structure):
    """Python counterpart of `scs_dvector_value_t` structure"""
    _fields_ = [('x', double_t),
                ('y', double_t),
                ('z', double_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class euler_t(Structure):
    """Python counterpart of `scs_value_euler_t` structure"""
    _fields_ = [('heading', float_t),
                ('pitch', float_t),
                ('roll', float_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class fplacement_t(Structure):
    """Python counterpart of `scs_value_fplacement_t` structure"""
    _fields_ = [('position', fvector_t),
                ('orientation', euler_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class dplacement_t(Structure):
    """Python counterpart of `scs_value_dplacement_t` structure"""
    _fields_ = [('position', dvector_t),
                ('orientation', euler_t),
                ('_padding', u32_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])
