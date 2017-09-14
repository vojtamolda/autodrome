import zmq
import capnp

from autodrome.common.telemetry_capnp import Bind, Response, Request


class Telemetry:

    Event = Response.Event

    def __init__(self, address: str=Bind.address):
        self.address = address
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(Bind.address)

    def receive(self) -> Response:
        request = Request.new_message()
        request_message = request.to_bytes()
        self.socket.send(request_message)
        reply_message = self.socket.recv()
        reply = Response.from_bytes(reply_message)
        return reply

    def wait(self, event: Event) -> Response:
        reply = self.receive()
        while reply.event != event:
            reply = self.receive()
        return reply

    def telemetry(self) -> Response.Telemetry:
        reply = self.wait(event=self.Event.frameEnd)
        return reply.data

