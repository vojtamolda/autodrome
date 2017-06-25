import zmq
import capnp
import unittest

import common.telemetry_capnp as telemetry


# region Unit Tests


class TestTelemetry(unittest.TestCase):

    @unittest.skip("Game has to be started manually")
    def test_telemetry(self):
        # 1. Start this test.
        # 2. Run ETS2/ATS with the telemetry plugin.
        # 3. Get into a truck and drive for a moment.
        # 4. Exit the game.

        context = zmq.Context()
        data_socket = context.socket(zmq.SUB)
        data_socket.setsockopt(zmq.SUBSCRIBE, bytes())
        data_socket.connect(telemetry.Bind.data)
        event_socket = context.socket(zmq.SUB)
        event_socket.setsockopt(zmq.SUBSCRIBE, bytes())
        event_socket.connect(telemetry.Bind.event)

        poller = zmq.Poller()
        poller.register(data_socket, flags=zmq.POLLIN)
        poller.register(event_socket, flags=zmq.POLLIN)

        count, event, events = 0, None, set()
        while event != 'shutdown':
            for socket, _ in poller.poll():
                if socket == data_socket:
                    message = data_socket.recv()
                    data = telemetry.Data.from_bytes(message)
                    count += 1
                if socket == event_socket:
                    message = event_socket.recv()
                    event = telemetry.Event.from_bytes(message).type
                    events.add(event)

        events.remove('init')  # ZMQ can be very peculiar, first PUB/SUB message is problematic.
        self.assertEqual(events, {'config', 'start', 'pause', 'shutdown'})
        self.assertGreater(count, 1)


# endregion
