import zmq
import enum
import struct
import unittest

import common.scstypes as scstypes


class Packet(scstypes.struct_t):
    """ Counterpart of the data structure sent by the ETS2/ATS telemetry plugin """
    _fields_ = [('placement', scstypes.dplacement_t),
                ('linear_velocity', scstypes.dvector_t),
                ('angular_velocity', scstypes.dvector_t),
                ('speed', scstypes.double_t),
                ('render_time', scstypes.timestamp_t),
                ('simulation_time', scstypes.timestamp_t),
                ('paused_simulation_time', scstypes.timestamp_t)]
    _type_ = "".join([field_type._type_ for (field_name, field_type) in _fields_])


class Event(enum.Enum):
    """ Counterpart of the event message sent by the ETS2/ATS telemetry plugin """
    INIT = b'init'
    CONFIG = b'config'
    START = b'start'
    PAUSE = b'pause'
    SHUTDOWN = b'shutdown'

    @classmethod
    def unpack(cls, buffer: bytes) -> object:
        """ Create a new instance by unpacking the provided `bytes` """
        return cls(buffer)


class Bind:
    """ Counterpart of ZeroMQ bindings to hosts and ports """
    packet = 'ipc:///tmp/telemetry.ipc'
    event = 'ipc:///tmp/event.ipc'


# region Unit Tests


class TestTelemetry(unittest.TestCase):

    def test_unpack(self):
        struct_format = 'ddd fff I ddd ddd d QQQ'.replace(' ', '')
        self.assertEqual(Packet._type_, struct_format)

        struct_values = list(range(len(struct_format)))
        struct_packed = struct.pack(struct_format, *struct_values)
        packet = Packet.unpack(struct_packed)

        self.assertEqual(packet.placement.position.x, 0)
        self.assertEqual(packet.placement.position.y, 1)
        self.assertEqual(packet.placement.position.z, 2)
        self.assertEqual(packet.placement.orientation.heading, 3)
        self.assertEqual(packet.placement.orientation.pitch, 4)
        self.assertEqual(packet.placement.orientation.roll, 5)
        self.assertEqual(packet.placement._padding, 6)

        self.assertEqual(packet.linear_velocity.x, 7)
        self.assertEqual(packet.linear_velocity.y, 8)
        self.assertEqual(packet.linear_velocity.z, 9)

        self.assertEqual(packet.angular_velocity.x, 10)
        self.assertEqual(packet.angular_velocity.y, 11)
        self.assertEqual(packet.angular_velocity.z, 12)

        self.assertEqual(packet.speed, 13)
        self.assertEqual(packet.render_time, 14)
        self.assertEqual(packet.simulation_time, 15)
        self.assertEqual(packet.paused_simulation_time, 16)

    # @unittest.skip("Game has to be started and shutdown manually")
    def test_telemetry(self):
        # copy libtelemetry.so into $(HOME)/Library/Application Support/Steam/steamapps/common/American Truck Simulator/American Truck Simulator.app/Contents/MacOS/plugins/
        # start this test
        # run $(HOME)/Library/Application Support/Steam/steamapps/common/American Truck Simulator/American Truck Simulator.app/Contents/MacOS/amtrucks
        # get into a truck and drive for a moment
        # exit the game

        event_socket = zmq.Context().socket(zmq.SUB)
        event_socket.setsockopt(zmq.SUBSCRIBE, bytes())
        event_socket.connect('ipc:///tmp/event.ipc')
        telemetry_socket = zmq.Context().socket(zmq.SUB)
        telemetry_socket.setsockopt(zmq.SUBSCRIBE, bytes())
        telemetry_socket.connect('ipc:///tmp/telemetry.ipc')

        events = []
        counter = 100
        for socket, message in poller.poll(timeout=10):
            if socket == event_socket:
                event = Event.unpack(message)
                events.append(event)
            if socket == telemetry_socket:
                packet = Packet.unpack(message)
                if counter == 0:
                    break
                counter -= 1

        self.assertListEqual(events, Event)
        self.assertEqual(counter, 0)


# endregion
