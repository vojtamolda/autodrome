#include "telemetry.hpp"


Telemetry::Telemetry(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version) :
    paused(true), game_log(params->common.log),
    zmq_context(1),
    event_socket(zmq_context, ZMQ_PUB), event_packet(),
    data_socket(zmq_context, ZMQ_PUB), data_packet()
{
    if (! this->check_version(params, version)) {
        throw exception();
    }

    this->register_event(params, SCS_TELEMETRY_EVENT_configuration, Telemetry::config_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_started, Telemetry::start_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_frame_start, Telemetry::frame_start_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_frame_end, Telemetry::frame_end_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_paused, Telemetry::pause_callback);

    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_world_placement, SCS_VALUE_TYPE_dplacement, this);
    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity, SCS_VALUE_TYPE_dvector, this);
    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity, SCS_VALUE_TYPE_dvector, this);
    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_speed, SCS_VALUE_TYPE_double, this);
    // SCS_TELEMETRY_TRUCK_CHANNEL_effective_steering
    // SCS_TELEMETRY_TRUCK_CHANNEL_effective_throttle
    // SCS_TELEMETRY_TRUCK_CHANNEL_effective_brake
    // SCS_TELEMETRY_TRUCK_CHANNEL_cruise_control
    // SCS_TELEMETRY_TRUCK_CHANNEL_lblinker
    // SCS_TELEMETRY_TRUCK_CHANNEL_rblinker
    // SCS_TELEMETRY_TRUCK_CHANNEL_navigation_speed_limit
    // ...

    this->data_packet.initRoot<Data>();
    this->data_socket.bind(Bind::DATA.toString());

    this->event_packet.initRoot<Event>();
    this->event_socket.bind(Bind::EVENT.toString());
    this->event_packet.getRoot<Event>().setType(Event::Type::INIT);
    this->event_socket.send(this->event_packet);
}

void Telemetry::config(const struct scs_telemetry_configuration_t *const config_info) {
    this->event_packet.getRoot<Event>().setType(Event::Type::CONFIG);
    this->event_socket.send(this->event_packet);
}

void Telemetry::start() {
    this->paused = false;

    this->event_packet.getRoot<Event>().setType(Event::Type::START);
    this->event_socket.send(this->event_packet);
}

void Telemetry::frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info) {
    if (this->paused) return;

    Data::Builder data = this->data_packet.getRoot<Data>();
    data.setPausedSimulationTime(frame_start_info->paused_simulation_time);
    data.setSimulationTime(frame_start_info->simulation_time);
    data.setRenderTime(frame_start_info->render_time);
}

void Telemetry::frame_end() {
    if (this->paused) return;

    this->data_socket.send(this->data_packet);
}

void Telemetry::pause() {
    this->paused = true;

    this->event_packet.getRoot<Event>().setType(Event::Type::PAUSE);
    this->event_socket.send(this->event_packet);
}

Telemetry::~Telemetry() {
    this->event_packet.getRoot<Event>().setType(Event::Type::SHUTDOWN);
    this->event_socket.send(this->event_packet);
}


SCSAPI_VOID Telemetry::config_callback(const scs_event_t event, const void *const event_info, const scs_context_t context) {
    const struct scs_telemetry_configuration_t *const config_info = static_cast<const scs_telemetry_configuration_t*>(event_info);
    static_cast<Telemetry*>(context)->config(config_info);
}

SCSAPI_VOID Telemetry::start_callback(const scs_event_t event, const void *const event_info, const scs_context_t context) {
    static_cast<Telemetry*>(context)->start();
}

SCSAPI_VOID Telemetry::frame_start_callback(const scs_event_t event, const void *const event_info, const scs_context_t context) {
    const struct scs_telemetry_frame_start_t *const frame_start_info = static_cast<const scs_telemetry_frame_start_t*>(event_info);
    static_cast<Telemetry*>(context)->frame_start(frame_start_info);
}

SCSAPI_VOID Telemetry::frame_end_callback(const scs_event_t event, const void *const event_info, const scs_context_t context) {
    static_cast<Telemetry*>(context)->frame_end();
}

SCSAPI_VOID Telemetry::pause_callback(const scs_event_t event, const void *const event_info, const scs_context_t context) {
    static_cast<Telemetry*>(context)->pause();
}

SCSAPI_VOID Telemetry::channel_update(const scs_string_t channel, const scs_u32_t index, const scs_value_t *const value, const scs_context_t context) {
    Data::Builder data = static_cast<Telemetry *>(context)->data_packet.getRoot<Data>();

    if (string(SCS_TELEMETRY_TRUCK_CHANNEL_world_placement) == channel) {
        Helper::set(data.getWorldPlacement(), value);
    } else if (string(SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity) == channel) {
        Helper::set(data.getLocalLinearVelocity(), value);
    } else if (string(SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity) == channel) {
        Helper::set(data.getLocalAngularVelocity(), value);
    } else if (string(SCS_TELEMETRY_TRUCK_CHANNEL_speed) == channel) {
        data.setSpeed(value->value_double.value);
    }
}


void Telemetry::Helper::set(DPlacement::Builder builder, const scs_value_t *const value) {
    assert(SCS_VALUE_TYPE_dplacement == value->type);
    scs_value_dplacement_t dplacement = value->value_dplacement;

    scs_value_t position_value = {.type = SCS_VALUE_TYPE_dvector, .value_dvector = dplacement.position};
    Helper::set(builder.getPosition(), &position_value);

    scs_value_t orientation_value = {.type = SCS_VALUE_TYPE_euler, .value_euler = dplacement.orientation};
    Helper::set(builder.getOrientation(), &orientation_value);
}

void Telemetry::Helper::set(FPlacement::Builder builder, const scs_value_t *const value) {
    assert(SCS_VALUE_TYPE_fplacement == value->type);
    scs_value_fplacement_t fplacement = value->value_fplacement;

    scs_value_t position_value = {.type = SCS_VALUE_TYPE_fvector, .value_fvector = fplacement.position};
    Helper::set(builder.getPosition(), &position_value);

    scs_value_t orientation_value = {.type = SCS_VALUE_TYPE_euler, .value_euler = fplacement.orientation};
    Helper::set(builder.getOrientation(), &orientation_value);
}

void Telemetry::Helper::set(Euler::Builder builder, const scs_value_t *const value) {
    assert(SCS_VALUE_TYPE_euler == value->type);
    scs_value_euler_t euler = value->value_euler;
    builder.setHeading(euler.heading);
    builder.setPitch(euler.pitch);
    builder.setRoll(euler.roll);
}

void Telemetry::Helper::set(DVector::Builder builder, const scs_value_t *const value) {
    assert(SCS_VALUE_TYPE_dvector == value->type);
    scs_value_dvector_t dvector = value->value_dvector;
    builder.setX(dvector.x);
    builder.setY(dvector.y);
    builder.setZ(dvector.z);
}

void Telemetry::Helper::set(FVector::Builder builder, const scs_value_t *const value) {
    assert(SCS_VALUE_TYPE_fvector == value->type);
    scs_value_fvector_t fvector = value->value_fvector;
    builder.setX(fvector.x);
    builder.setY(fvector.y);
    builder.setZ(fvector.z);
}


Telemetry::capnp_socket_t::capnp_socket_t(context_t& context, int type) :
        socket_t(context, type)
{/*   ¯\(°_o)/¯   */}

size_t Telemetry::capnp_socket_t::send(capnp::MessageBuilder &message) {
    auto words = capnp::messageToFlatArray(message);
    auto bytes = words.asBytes();
    return socket_t::send(bytes.begin(), bytes.size(), 0);
}


void Telemetry::log(const string& message, const scs_log_type_t type) const {
    if (!this->game_log) return;
    this->game_log(type, message.c_str());
}

bool Telemetry::check_version(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version) const {
    if (version != SCS_TELEMETRY_VERSION_1_00) {
        return false;
    }

    if (string(SCS_GAME_ID_EUT2) == params->common.game_id) {
        const scs_u32_t MINIMAL_VERSION = SCS_TELEMETRY_EUT2_GAME_VERSION_1_00;
        if (params->common.game_version < MINIMAL_VERSION) {
            this->log("[autodrome] : incompatible (old) version of the game, please, update the game", SCS_LOG_TYPE_error);
            return false;
        }
        const scs_u32_t IMPLEMENTED_VERSION = SCS_TELEMETRY_EUT2_GAME_VERSION_CURRENT;
        if (SCS_GET_MAJOR_VERSION(params->common.game_version) > SCS_GET_MAJOR_VERSION(IMPLEMENTED_VERSION)) {
            this->log("[autodrome] : incompatible (old) version of the telemetry SDK, please, update the SDK", SCS_LOG_TYPE_error);
            return false;
        }
    }

    if (string(SCS_GAME_ID_ATS) == params->common.game_id) {
        const scs_u32_t MINIMAL_VERSION = SCS_TELEMETRY_ATS_GAME_VERSION_1_00;
        if (params->common.game_version < MINIMAL_VERSION) {
            this->log("[autodrome] : incompatible (old) version of the game, please, update the game", SCS_LOG_TYPE_error);
            return false;
        }
        const scs_u32_t IMPLEMENTED_VERSION = SCS_TELEMETRY_ATS_GAME_VERSION_CURRENT;
        if (SCS_GET_MAJOR_VERSION(params->common.game_version) > SCS_GET_MAJOR_VERSION(IMPLEMENTED_VERSION)) {
            this->log("[autodrome] : incompatible (old) version of the telemetry SDK, please, update the SDK", SCS_LOG_TYPE_error);
            return false;
        }
    }

    return true;
}

bool Telemetry::register_event(const scs_telemetry_init_params_v100_t *const params, const scs_event_t event, const scs_telemetry_event_callback_t callback) {
    if (params->register_for_event(event, callback, this) != SCS_RESULT_ok) {
        string message = "[autodrome] : unable to register for scs_event_t=" + to_string(event) + " event callback";
        this->log(message, SCS_LOG_TYPE_error);
        return false;
    }
    return true;
}

bool Telemetry::register_channel(const scs_telemetry_init_params_v100_t *const params, const scs_string_t channel, const scs_value_type_t type, const scs_context_t context) {
    if (params->register_for_channel(channel, SCS_U32_NIL, type, SCS_TELEMETRY_CHANNEL_FLAG_none, Telemetry::channel_update, context) != SCS_RESULT_ok) {
        string message = "[autodrome] : unable to register for scs_telemetry_t=" + string(channel) + "' channel update";
        this->log(message, SCS_LOG_TYPE_error);
        return false;
    }
    return true;
}
