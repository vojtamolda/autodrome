#include "telemetry.hpp"


Telemetry::Telemetry(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version) :
    paused(true), game_log(params->common.log),
    zmq_context(1), zmq_event(zmq_context, ZMQ_PUB), zmq_telemetry(zmq_context, ZMQ_PUB),
    packet()
{
    if (! this->check_version(params, version)) {
        throw exception();
    }

    this->register_event(params, SCS_TELEMETRY_EVENT_configuration, Telemetry::config_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_started, Telemetry::start_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_frame_start, Telemetry::frame_start_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_frame_end, Telemetry::frame_end_callback);
    this->register_event(params, SCS_TELEMETRY_EVENT_paused, Telemetry::pause_callback);

    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_world_placement, SCS_VALUE_TYPE_dplacement, &(this->packet.placement));
    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity, SCS_VALUE_TYPE_dvector, &(this->packet.linear_velocity));
    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity, SCS_VALUE_TYPE_dvector, &(this->packet.angular_velocity));
    this->register_channel(params, SCS_TELEMETRY_TRUCK_CHANNEL_speed, SCS_VALUE_TYPE_double, &(this->packet.speed));
    // SCS_TELEMETRY_TRUCK_CHANNEL_effective_steering
    // SCS_TELEMETRY_TRUCK_CHANNEL_effective_throttle
    // SCS_TELEMETRY_TRUCK_CHANNEL_effective_brake
    // SCS_TELEMETRY_TRUCK_CHANNEL_cruise_control
    // SCS_TELEMETRY_TRUCK_CHANNEL_lblinker
    // SCS_TELEMETRY_TRUCK_CHANNEL_rblinker
    // SCS_TELEMETRY_TRUCK_CHANNEL_navigation_speed_limit

    this->zmq_event.bind("ipc:///tmp/event.ipc");
    this->zmq_telemetry.bind("ipc:///tmp/telemetry.ipc");

    publish_t message("init");
    this->zmq_event.send(message);
}

void Telemetry::config(const struct scs_telemetry_configuration_t *const config_info) {
    publish_t message("config");
    this->zmq_event.send(message);
}

void Telemetry::start() {
    this->paused = false;

    publish_t message("start");
    this->zmq_event.send(message);
}

void Telemetry::frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info) {
    if (this->paused) return;

    this->packet.render_time = frame_start_info->render_time;
    this->packet.simulation_time = frame_start_info->simulation_time;
    this->packet.paused_simulation_time = frame_start_info->paused_simulation_time;
}

void Telemetry::frame_end() {
    if (this->paused) return;

    publish_t message(this->packet);
    this->zmq_telemetry.send(message);
}

void Telemetry::pause() {
    this->paused = true;

    publish_t message("pause");
    this->zmq_event.send(message);
}

Telemetry::~Telemetry() {
    publish_t message("shutdown");
    this->zmq_event.send(message);
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
    switch (value->type) {
        case SCS_VALUE_TYPE_string: {
            scs_string_t *const storage = static_cast<scs_string_t *>(context);
            *storage = value->value_string.value;
            break;
        }
        case SCS_VALUE_TYPE_dplacement: {
            scs_value_dplacement_t *const storage = static_cast<scs_value_dplacement_t *>(context);
            *storage = value->value_dplacement;
            break;
        }
        case SCS_VALUE_TYPE_fplacement: {
            scs_value_fplacement_t *const storage = static_cast<scs_value_fplacement_t *>(context);
            *storage = value->value_fplacement;
            break;
        }
        case SCS_VALUE_TYPE_euler: {
            scs_value_euler_t *const storage = static_cast<scs_value_euler_t *>(context);
            *storage = value->value_euler;
            break;
        }
        case SCS_VALUE_TYPE_dvector: {
            scs_value_dvector_t *const storage = static_cast<scs_value_dvector_t *>(context);
            *storage = value->value_dvector;
            break;
        }
        case SCS_VALUE_TYPE_fvector: {
            scs_value_fvector_t *const storage = static_cast<scs_value_fvector_t *>(context);
            *storage = value->value_fvector;
            break;
        }
        case SCS_VALUE_TYPE_double: {
            scs_double_t *const storage = static_cast<scs_double_t *>(context);
            *storage = value->value_double.value;
            break;
        }
        case SCS_VALUE_TYPE_u64: {
            scs_u64_t *const storage = static_cast<scs_u64_t *>(context);
            *storage = value->value_u64.value;
            break;
        }
        case SCS_VALUE_TYPE_u32: {
            scs_u32_t *const storage = static_cast<scs_u32_t *>(context);
            *storage = value->value_u32.value;
            break;
        }
        case SCS_VALUE_TYPE_s32: {
            scs_s32_t *const storage = static_cast<scs_s32_t *>(context);
            *storage = value->value_s32.value;
            break;
        }
        case SCS_VALUE_TYPE_bool: {
            scs_u8_t *const storage = static_cast<scs_u8_t *>(context);
            *storage = value->value_bool.value;
            break;
        }
    }
}

void Telemetry::log(const string& message, const scs_log_type_t type) const {
    if (! this->game_log) return;
    this->game_log(type, message.c_str());
}

bool Telemetry::check_version(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version) const {
    if (version != SCS_TELEMETRY_VERSION_1_00) {
        return false;
    }

    if (string(SCS_GAME_ID_EUT2) == params->common.game_id) {
        const scs_u32_t MINIMAL_VERSION = SCS_TELEMETRY_EUT2_GAME_VERSION_1_00;
        if (params->common.game_version < MINIMAL_VERSION) {
            this->log("[polygon] : incompatible (old) version of the game, please, update the game", SCS_LOG_TYPE_error);
            return false;
        }
        const scs_u32_t IMPLEMENTED_VERSION = SCS_TELEMETRY_EUT2_GAME_VERSION_CURRENT;
        if (SCS_GET_MAJOR_VERSION(params->common.game_version) > SCS_GET_MAJOR_VERSION(IMPLEMENTED_VERSION)) {
            this->log("[polygon] : incompatible (old) version of the telemetry SDK, please, update the SDK", SCS_LOG_TYPE_error);
            return false;
        }
    }

    if (string(SCS_GAME_ID_ATS) == params->common.game_id) {
        const scs_u32_t MINIMAL_VERSION = SCS_TELEMETRY_ATS_GAME_VERSION_1_00;
        if (params->common.game_version < MINIMAL_VERSION) {
            this->log("[polygon] : incompatible (old) version of the game, please, update the game", SCS_LOG_TYPE_error);
            return false;
        }
        const scs_u32_t IMPLEMENTED_VERSION = SCS_TELEMETRY_ATS_GAME_VERSION_CURRENT;
        if (SCS_GET_MAJOR_VERSION(params->common.game_version) > SCS_GET_MAJOR_VERSION(IMPLEMENTED_VERSION)) {
            this->log("[polygon] : incompatible (old) version of the telemetry SDK, please, update the SDK", SCS_LOG_TYPE_error);
            return false;
        }
    }

    return true;
}

bool Telemetry::register_event(const scs_telemetry_init_params_v100_t *const params, const scs_event_t event, const scs_telemetry_event_callback_t callback) {
    if (params->register_for_event(event, callback, this) != SCS_RESULT_ok) {
        string message = "[polygon] : unable to register for scs_event_t=" + to_string(event) + " event callback";
        this->log(message, SCS_LOG_TYPE_error);
        return false;
    }
    return true;
}

bool Telemetry::register_channel(const scs_telemetry_init_params_v100_t *const params, const scs_string_t channel, const scs_value_type_t type, const scs_context_t context) {
    if (params->register_for_channel(channel, SCS_U32_NIL, type, SCS_TELEMETRY_CHANNEL_FLAG_none, Telemetry::channel_update, context) != SCS_RESULT_ok) {
        string message = "[polygon] : unable to register for scs_telemetry_t=" + string(channel) + "' channel update";
        this->log(message, SCS_LOG_TYPE_error);
        return false;
    }
    return true;
}
