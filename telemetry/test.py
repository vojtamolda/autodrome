import zmq
import struct
import unittest

from telemetry import Packet


class TestTelemetry(unittest.TestCase):
    def test_unpack(self):
        struct_format = 'ddd fff I ddd ddd d LLL'
        struct_format = struct_format.replace(' ', '')
        self.assertEqual(Packet._type_, struct_format)

        struct_values = list(range(len(struct_format)))
        struct_packed = struct.pack(struct_format, *struct_values)
        packet = Packet(struct_packed)

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

    @unittest.skip("Game has to be started and shutdown manually")
    def test_telemetry(self):
        # copy libtelemetry.so into $(HOME)/Library/Application Support/Steam/steamapps/common/American Truck Simulator/American Truck Simulator.app/Contents/MacOS/plugins/
        # start this test
        # run $(HOME)/Library/Application Support/Steam/steamapps/common/American Truck Simulator/American Truck Simulator.app/Contents/MacOS/amtrucks
        # get into a truck and drive for a momement
        # exit the game

        event_socket = zmq.Context().socket(zmq.SUB)
        event_socket.setsockopt(zmq.SUBSCRIBE, bytes())
        event_socket.connect('ipc:///tmp/event.ipc')
        telemetry_socket = zmq.Context().socket(zmq.SUB)
        telemetry_socket.setsockopt(zmq.SUBSCRIBE, bytes())
        telemetry_socket.connect('ipc:///tmp/telemetry.ipc')

        config, start, telemetry, pause, shutdown = False, False, False, False, False
        while True:
            recieved_event = event_socket.recv()
            if recieved_event == b'config':
                config = True
            if recieved_event == b'start':
                start = True
                for counter in range(100):
                    message = telemetry_socket.recv()
                    packet = Packet(message)
                telemetry = True
            if recieved_event == b'pause':
                pause = True
            if recieved_event == b'shutdown':
                shutdown = True
                break

        self.assertTrue(config)
        self.assertTrue(start)
        self.assertTrue(telemetry)
        self.assertTrue(pause)
        self.assertTrue(shutdown)
