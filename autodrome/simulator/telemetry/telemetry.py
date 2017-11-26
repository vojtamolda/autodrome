import zmq
import math
import time
import capnp
from pathlib import Path


class Telemetry:
    Message = capnp.load(str(Path(__file__).parent / 'share' / 'message.capnp'))
    Request = Message.Request
    Response = Message.Response
    Event = Response.Event
    Data = Response.Telemetry

    def __init__(self, address: str=Message.Bind.address):
        self.address = address
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(Telemetry.Message.Bind.address)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, flags=zmq.POLLIN)

        request = self.Request.new_message()
        request_bytes = request.to_bytes()
        self.socket.send(request_bytes)

    def recv(self) -> Response:
        reply_bytes = self.socket.recv()
        reply = self.Response.from_bytes(reply_bytes)

        request = self.Request.new_message()
        request_bytes = request.to_bytes()
        self.socket.send(request_bytes)
        return reply

    def wait(self, event: Event, timeout: float=math.inf) -> Response:
        reply, deadline = None, time.time() + timeout
        while time.time() < deadline:
            if self.poller.poll(timeout=5):
                reply = self.recv()
            if reply and reply.event == event:
                break
        return reply

    def data(self) -> Data:
        reply = self.wait(event=Telemetry.Event.frameEnd)
        return reply.data.telemetry
