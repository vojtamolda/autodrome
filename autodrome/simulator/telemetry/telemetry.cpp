#include "telemetry.hpp"


Telemetry::Telemetry(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version) :
    paused(true), print(params->common.log),
    zmq_context(1), data_socket(zmq_context, ZMQ_REP), message_builder()
{
    if (!this->check_version(params, version)) {
        throw exception();
    }
    if (!this->check_steamid()) {
        this->data_socket.close();
        this->zmq_context.close();
        return;
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

    this->data_socket.bind(Bind::ADDRESS.toString());
    auto response = this->message_builder.initRoot<Response>();
    response.initData();

    //auto request = this->socket.recv();
    auto message = message_t();
    auto sock = (socket_t*) &(this->data_socket);
    sock->recv(&message);
    response.setEvent(Response::Event::LOAD);
    response.getData().setNone();
    this->data_socket.send(this->message_builder);
}

void Telemetry::config(const struct scs_telemetry_configuration_t *const config_info) {
    auto request = this->data_socket.recv();
    auto response = this->message_builder.getRoot<Response>();
    response.setEvent(Response::Event::CONFIG);
    auto config = response.getData().initConfig();
    config.setNotImplemented();
    this->data_socket.send(this->message_builder);
}

void Telemetry::start() {
    this->paused = false;

    auto request = this->data_socket.recv();
    auto response = this->message_builder.getRoot<Response>();
    response.setEvent(Response::Event::START);
    response.getData().setNone();
    this->data_socket.send(this->message_builder);
}

void Telemetry::frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info) {
    if (this->paused) return;

    auto request = this->data_socket.recv();
    auto response = this->message_builder.getRoot<Response>();
    response.setEvent(Response::Event::FRAME_START);
    response.getData().setNone();
    this->data_socket.send(this->message_builder);

    // Prepare telemetry data for channel_update(...) callbacks
    auto telemetry = response.getData().initTelemetry();
    telemetry.setPausedSimulationTime(frame_start_info->paused_simulation_time);
    telemetry.setSimulationTime(frame_start_info->simulation_time);
    telemetry.setRenderTime(frame_start_info->render_time);
}

void Telemetry::frame_end() {
    if (this->paused) return;

    auto request = this->data_socket.recv();
    auto response = this->message_builder.getRoot<Response>();
    response.setEvent(Response::Event::FRAME_END);
    // Telemetry data were set by channel_update(...) callbacks
    this->data_socket.send(this->message_builder);
}

void Telemetry::pause() {
    this->paused = true;

    auto request = this->data_socket.recv();
    auto response = this->message_builder.getRoot<Response>();
    response.setEvent(Response::Event::PAUSE);
    response.getData().setNone();
    this->data_socket.send(this->message_builder);
}

Telemetry::~Telemetry() {
    if (! this->zmq_context) return;

    auto request = this->data_socket.recv();
    auto response = this->message_builder.getRoot<Response>();
    response.setEvent(Response::Event::UNLOAD);
    response.getData().setNone();
    this->data_socket.send(this->message_builder);

    this->data_socket.unbind(*Bind::ADDRESS);
    this->data_socket.close();
    this->zmq_context.close();
}


SCSAPI_VOID Telemetry::config_callback(const scs_event_t event, const void *const event_info, scs_context_t const context) {
    const auto config_info = static_cast<const scs_telemetry_configuration_t*>(event_info);
    static_cast<Telemetry*>(context)->config(config_info);
}

SCSAPI_VOID Telemetry::start_callback(const scs_event_t event, const void *const event_info, scs_context_t const context) {
    static_cast<Telemetry*>(context)->start();
}

SCSAPI_VOID Telemetry::frame_start_callback(const scs_event_t event, const void *const event_info, scs_context_t const context) {
    const auto frame_start_info = static_cast<const scs_telemetry_frame_start_t*>(event_info);
    static_cast<Telemetry*>(context)->frame_start(frame_start_info);
}

SCSAPI_VOID Telemetry::frame_end_callback(const scs_event_t event, const void *const event_info, scs_context_t const context) {
    static_cast<Telemetry*>(context)->frame_end();
}

SCSAPI_VOID Telemetry::pause_callback(const scs_event_t event, const void *const event_info, scs_context_t const context) {
    static_cast<Telemetry *>(context)->pause();
}

SCSAPI_VOID Telemetry::channel_update(const scs_string_t channel, const scs_u32_t index, const scs_value_t *const value, const scs_context_t context) {
    Telemetry* self = static_cast<Telemetry *>(context);
    auto response = self->message_builder.getRoot<Response>();
    auto telemetry = response.getData().getTelemetry();

    if (string(SCS_TELEMETRY_TRUCK_CHANNEL_world_placement) == channel) {
        Helper::set(telemetry.getWorldPlacement(), value);
    } else if (string(SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity) == channel) {
        Helper::set(telemetry.getLocalLinearVelocity(), value);
    } else if (string(SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity) == channel) {
        Helper::set(telemetry.getLocalAngularVelocity(), value);
    } else if (string(SCS_TELEMETRY_TRUCK_CHANNEL_speed) == channel) {
        telemetry.setSpeed(value->value_double.value);
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
    try {
        auto words = capnp::messageToFlatArray(message);
        auto bytes = words.asBytes();
        return socket_t::send(bytes.begin(), bytes.size(), 0);
    } catch (zmq::error_t &error) {
        return 0;
        // this->log("[autodrome] : error during zmq recv(...)");
    }
}

unique_ptr<message_t> Telemetry::capnp_socket_t::recv() {
    try {
        auto message = unique_ptr<message_t>(new message_t());
        socket_t::recv(message.get());
        return message;
    } catch (zmq::error_t &error) {
        return unique_ptr<message_t>(new message_t());
        // this->log("[autodrome] : error during zmq recv(...)");
    }
}


void Telemetry::log(const string& message, const scs_log_type_t type) const {
    if (!this->print) return;
    this->print(type, message.c_str());
}

#include <unistd.h>

bool Telemetry::check_steamid() const {
    ifstream steam_appid_file("MacOS/steam_appid.txt");
    if (steam_appid_file.is_open()) {
        steam_appid_file.close();
        return true;
    } else {
        this->log("[autodrome] : disabling telemetry SDK, standalone run detected", SCS_LOG_TYPE_warning);
        return false;
    }
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
