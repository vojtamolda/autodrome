"""Definition of Python counterparts to C data structures published by the ETS2/ATS game telemetry plugin"""

import common.scstypes as scstypes


class Packet(scstypes.Structure):
    """Python counterpart of the data structure published by the telemetry SDK pluging"""
    _fields_ = [('placement', scstypes.dplacement_t),
                ('linear_velocity', scstypes.dvector_t),
                ('angular_velocity', scstypes.dvector_t),
                ('speed', scstypes.double_t),
                ('render_time', scstypes.timestamp_t),
                ('simulation_time', scstypes.timestamp_t),
                ('paused_simulation_time', scstypes.timestamp_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])
