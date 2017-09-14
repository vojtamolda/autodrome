import zmq
import capnp


class Telemetry:
    Message = capnp.load('autodrome/simulator/telemetry/share/message.capnp')
    Event = Message.Response.Event
    Data = Message.Response.Telemetry

    def __init__(self, address: str=Message.Bind.address):
        self.address = address
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(Telemetry.Message.Bind.address)

    def receive(self) -> Message.Response:
        request = self.Message.Request.new_message()
        request_message = request.to_bytes()
        self.socket.send(request_message)
        reply_message = self.socket.recv()
        reply = Telemetry.Message.Response.from_bytes(reply_message)
        return reply

    def wait(self, event: Event) -> Message.Response:
        reply = self.receive()
        while reply.event != event:
            reply = self.receive()
        return reply

    def data(self) -> Data:
        reply = self.wait(event=Telemetry.Event.frameEnd)
        return reply.data.telemetry
