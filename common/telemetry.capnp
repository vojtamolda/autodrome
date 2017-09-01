@0xacb284c4d8d75176;

using SCS = import "scs.capnp";


# Socket binding location for ZMQ REQ/REP telemetry messaging
struct Bind {
  const address :Text = "ipc:///tmp/autodrome_telemetry.ipc";
}


# Response packet sent by the ETS2/ATS telemetry plugin
struct Response {
  event @0: Event;
  data: union {
    none @1: Void;
    config @2: Config;
    telemetry @3: Telemetry;
  }

  # Lifecycle event
  enum Event {
    load @0;
    config @1;
    start @2;
    frameStart @3;
    frameEnd @4;
    pause @5;
    unload @6;
  }

  # Truck configuration
  struct Config {
    notImplemented @0: Void;
  }

  # Telemetry data
  struct Telemetry {
    worldPlacement @0 :SCS.DPlacement;
    localLinearVelocity @1 :SCS.DVector;
    localAngularVelocity @2 :SCS.DVector;
    speed @3 :SCS.Float;
    renderTime @4: SCS.Timestamp;
    simulationTime @5: SCS.Timestamp;
    pausedSimulationTime @6: SCS.Timestamp;
  }
}


# Request packet sent to the ETS2/ATS telemetry plugin
struct Request {
  okay @0: Void;
}
