import struct


class struct_t(dict):
    """ Structure that can unpack itself from byte arrays with fields accessible via dot.notation """

    def __init__(self, values):
        """ Initialize fields from a dictionary or from a list of values """
        if isinstance(values, dict):
            fields = values
        else:
            fields = {}
            for (field_name, field_type), field_value in zip(self._fields_, values):
                fields[field_name] = field_type(field_value)
        super().__init__(fields)

    def __getattr__(self, item):
        """ Interface to access the structure members via dot.notation """
        return self[item] if item in self else None

    @classmethod
    def unpack(cls, buffer: bytes) -> object:
        """ Create a new instance and initialize all field values by unpacking the provided `bytes` """
        if cls._fields_ is None or cls._type_ is None:
            raise AttributeError("Attributes needed for unpacking are not implemented")

        if isinstance(buffer, bytes):
            unpacked_values = struct.unpack(cls._type_, buffer)
            field_values = iter(unpacked_values)
        else:
            field_values = buffer

        members = {}
        for (field_name, field_type) in cls._fields_:
            if issubclass(field_type, struct_t):
                substructure = field_type.unpack(field_values)
                members[field_name] = substructure
            else:
                primitive = field_type(next(field_values))
                members[field_name] = primitive
        return cls(members)


class u8_t(int):
    """ Counterpart of `scs_u8_t` """
    _type_ = 'B'


class u16_t(int):
    """ Counterpart of `scs_u16_t` """
    _type_ = 'H'


class s16_t(int):
    """ Counterpart of `scs_s16_t` """
    _type_ = 'h'


class u32_t(int):
    """ Counterpart of `scs_u32_t` """
    _type_ = 'I'


class s32_t(int):
    """ Counterpart of `scs_s32_t` """
    _type_ = 'i'


class u64_t(int):
    """ Counterpart of `scs_u64_t` """
    _type_ = 'Q'


class s64_t(int):
    """ Counterpart of `scs_s64_t` """
    _type_ = 'q'


class float_t(float):
    """ Counterpart of `scs_float_t` """
    _type_ = 'f'


class double_t(float):
    """ Counterpart of `scs_double_t` """
    _type_ = 'd'


class string_t(str):
    """ Counterpart of `scs_string_t` """
    pass


class timestamp_t(u64_t):
    """ Counterpart of `scs_timestamp_t` """
    pass


class array_t(list):
    """ Counterpart of `scs_array_t` array """
    pass


class float2_t(struct_t):
    """ Counterpart of `scs_fixed2_t` structure """
    _fields_ = [('x', float_t), ('y', float_t)]


class float3_t(struct_t):
    """ Counterpart of `scs_fixed3_t` structure """
    _fields_ = [('x', float_t), ('y', float_t), ('z', float_t)]


class float4_t(tuple):
    """Counterpart of `scs_float4_t` structure"""
    pass


class quaternion_t(struct_t):
    """ Counterpart of `scs_quaternion_t` structure """
    _fields_ = [('w', float_t), ('x', float_t), ('y', float_t), ('z', float_t)]


class fvector_t(struct_t):
    """ Counterpart of `scs_fvector_value_t` structure """
    _fields_ = [('x', float_t), ('y', float_t), ('z', float_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class dvector_t(struct_t):
    """ Counterpart of `scs_dvector_value_t` structure """
    _fields_ = [('x', double_t), ('y', double_t), ('z', double_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class euler_t(struct_t):
    """ Counterpart of `scs_value_euler_t` structure """
    _fields_ = [('heading', float_t), ('pitch', float_t), ('roll', float_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class fplacement_t(struct_t):
    """ Counterpart of `scs_value_fplacement_t` structure """
    _fields_ = [('position', fvector_t), ('orientation', euler_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class dplacement_t(struct_t):
    """ Counterpart of `scs_value_dplacement_t` structure """
    _fields_ = [('position', dvector_t), ('orientation', euler_t), ('_padding', u32_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])
