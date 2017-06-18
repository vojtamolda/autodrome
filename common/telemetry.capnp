@0xacb284c4d8d75176;

using SCS = import "scs.capnp";

# Socket binding locations for ZMQ PUB/SUB messaging system
struct Bind {
    const data :Text = "ipc:///tmp/telemetry_data.ipc";
    const event :Text = "ipc:///tmp/telemetry_event.ipc";
}

# Game data sent by the ETS2/ATS telemetry plugin
struct Data {
  worldPlacement @0 :SCS.DPlacement;
  localLinearVelocity @1 :SCS.DVector;
  localAngularVelocity @2 :SCS.DVector;
  speed @3 :SCS.Float;
  renderTime @4: SCS.Timestamp;
  simulationTime @5: SCS.Timestamp;
  pausedSimulationTime @6: SCS.Timestamp;
}

# Game event emitted by the ETS2/ATS telemetry plugin
struct Event {
  type @0: Type;
  enum Type {
    init @0;
    config @1;
    start @2;
    pause @3;
    shutdown @4;
  }
}
