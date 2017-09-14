@0xacb284c4d8d75176;

using SCS = import "scs.capnp";


# Socket binding location for ZMQ REQ/REP telemetry messaging
struct Bind {
  const address :Text = "ipc:///tmp/autodrome_telemetry.ipc";
}


# Response packet sent by the ETS2/ATS telemetry plugin
struct Response {
  event @0 :Event;
  data :union {
    none @1 :Void;
    config @2 :Config;
    telemetry @3 :Telemetry;
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
    notImplemented @0 :Void;
  }

  # Telemetry data
  struct Telemetry {
    renderTime @0 :SCS.Timestamp;
    simulationTime @1 :SCS.Timestamp;
    pausedSimulationTime @2 :SCS.Timestamp;

    worldPlacement @3 :SCS.DPlacement;
    localLinearVelocity @4 :SCS.DVector;
    localAngularVelocity @5 :SCS.DVector;
    speed @6 :SCS.Float;

    effectiveSteering @7 :SCS.Float;
    effectiveThrottle @8 :SCS.Float;
    effectiveBrake @9 :SCS.Float;
    parkingBrake @10 :SCS.Bool;

    wearEngine @11 :SCS.Float;
    wearTransmission @12 :SCS.Float;
    wearCabin @13 :SCS.Float;
    wearChassis @14 :SCS.Float;
  }
}


# Request packet sent to the ETS2/ATS telemetry plugin
struct Request {
  okay @0 :Void;
}
