#include "telemetry.hpp"


Telemetry::Telemetry(const scs_telemetry_init_params_v100_t *const params) :
    paused(true), game_log(params->common.log),

    world_placement{.position={.x=0.0, .y=0.0, .z=0.0},
                    .orientation={.heading=0.0, .pitch=0.0, .roll=0.0}, SCS_U32_NIL},
    local_linear_velocity{.x=0.0, .y=0.0, .z=0.0},
    local_angular_velocity{.x=0.0, .y=0.0, .z=0.0},
    speed{0.0},

    render_time(0), simulation_time(0), paused_simulation_time(0)
{
	if (params->register_for_event(SCS_TELEMETRY_EVENT_configuration, Telemetry::configuration_callback, this) != SCS_RESULT_ok) {
	    this->log("Unable to register 'configuration' event callback", SCS_LOG_TYPE_error);
	}
	if (params->register_for_event(SCS_TELEMETRY_EVENT_started, Telemetry::start_callback, this) != SCS_RESULT_ok) {
	    this->log("Unable to register 'started' event callback", SCS_LOG_TYPE_error);
	}
	if (params->register_for_event(SCS_TELEMETRY_EVENT_frame_start, Telemetry::frame_start_callback, this) != SCS_RESULT_ok) {
	    this->log("Unable to register 'frame_start' event callback", SCS_LOG_TYPE_error);
	}
	if (params->register_for_event(SCS_TELEMETRY_EVENT_frame_end, Telemetry::frame_end_callback, this) != SCS_RESULT_ok) {
	    this->log("Unable to register 'frame_end' event callback", SCS_LOG_TYPE_error);
	}
	if (params->register_for_event(SCS_TELEMETRY_EVENT_paused, Telemetry::pause_callback, this) != SCS_RESULT_ok) {
	    this->log("Unable to register 'paused' event callback", SCS_LOG_TYPE_error);
	}

	if (params->register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_world_placement, SCS_U32_NIL, SCS_VALUE_TYPE_dplacement,
	            SCS_TELEMETRY_CHANNEL_FLAG_none, Telemetry::channel_update, &(this->world_placement)) != SCS_RESULT_ok) {
	    string message = "Unable to register for '" + string(SCS_TELEMETRY_TRUCK_CHANNEL_world_placement) + "' channel update";
	    this->log(message.c_str(), SCS_LOG_TYPE_error);
	}
	if (params->register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity, SCS_U32_NIL, SCS_VALUE_TYPE_dvector,
	            SCS_TELEMETRY_CHANNEL_FLAG_none, Telemetry::channel_update, &(this->local_linear_velocity)) != SCS_RESULT_ok) {
	    string message = "Unable to register for '" + string(SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity) + "' channel update";
	    this->log(message.c_str(), SCS_LOG_TYPE_error);
	}
	if (params->register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity, SCS_U32_NIL, SCS_VALUE_TYPE_dvector,
	            SCS_TELEMETRY_CHANNEL_FLAG_none, Telemetry::channel_update, &(this->local_angular_velocity)) != SCS_RESULT_ok) {
	    string message = "Unable to register for '" + string(SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity) + "' channel update";
	    this->log(message.c_str(), SCS_LOG_TYPE_error);
	}
	if (params->register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_speed, SCS_U32_NIL, SCS_VALUE_TYPE_double,
	            SCS_TELEMETRY_CHANNEL_FLAG_none, Telemetry::channel_update, &(this->speed)) != SCS_RESULT_ok) {
	    string message = "Unable to register for '" + string(SCS_TELEMETRY_TRUCK_CHANNEL_speed) + "' channel update";
	    this->log(message.c_str(), SCS_LOG_TYPE_error);
	}
	// SCS_TELEMETRY_TRUCK_CHANNEL_effective_steering
	// SCS_TELEMETRY_TRUCK_CHANNEL_effective_throttle
	// SCS_TELEMETRY_TRUCK_CHANNEL_effective_brake
	// SCS_TELEMETRY_TRUCK_CHANNEL_cruise_control
	// SCS_TELEMETRY_TRUCK_CHANNEL_lblinker
	// SCS_TELEMETRY_TRUCK_CHANNEL_rblinker
	// SCS_TELEMETRY_TRUCK_CHANNEL_navigation_speed_limit
}

void Telemetry::configuration(const struct scs_telemetry_configuration_t *const configuration_info) {

}

void Telemetry::start() {
    this->paused = false;
}

void Telemetry::frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info) {
    this->render_time = frame_start_info->render_time;
    this->simulation_time = frame_start_info->simulation_time;
    this->paused_simulation_time = frame_start_info->paused_simulation_time;
}

void Telemetry::frame_end() {
	if (this->paused) return;

    // TODO: Publish the fresh telemetry data here...
}

void Telemetry::pause() {
    this->paused = true;
}

SCSAPI_VOID Telemetry::configuration_callback(const scs_event_t event, const void *const event_info, const scs_context_t context) {
    const struct scs_telemetry_configuration_t *const configuration_info = static_cast<const scs_telemetry_configuration_t*>(event_info);
    static_cast<Telemetry*>(context)->configuration(configuration_info);
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

SCSAPI_VOID Telemetry::channel_update(const scs_string_t name, const scs_u32_t index, const scs_value_t *const value, const scs_context_t context) {
    switch (value->type) {
        case SCS_VALUE_TYPE_dplacement: {
            scs_value_dplacement_t *const storage = static_cast<scs_value_dplacement_t *>(context);
            *storage = value->value_dplacement;
            break;
        }
        case SCS_VALUE_TYPE_dvector: {
            scs_value_dvector_t *const storage = static_cast<scs_value_dvector_t *>(context);
            *storage = value->value_dvector;
            break;
        }
        case SCS_VALUE_TYPE_double: {
            scs_value_double_t *const storage = static_cast<scs_value_double_t *>(context);
            *storage = value->value_double;
            break;
        }
        default: {
            // There's no easy way to complain into the this->log from here... :-(
            break;
        }
    }
}

Telemetry::~Telemetry() {
    this->game_log = NULL;
    this->paused = true;
}

void Telemetry::log(const scs_string_t message, const scs_log_type_t type) {
    this->game_log(type, message);
}

bool Telemetry::compatible_version(const scs_telemetry_init_params_v100_t *const params) {
	if (string(SCS_GAME_ID_EUT2) == params->common.game_id) {
		const scs_u32_t MINIMAL_VERSION = SCS_TELEMETRY_EUT2_GAME_VERSION_1_00;
		if (params->common.game_version < MINIMAL_VERSION) {
			params->common.log(SCS_LOG_TYPE_error, "Incompatible (old) version of the game. Please update the game.");
			return false;
		}
		const scs_u32_t IMPLEMENTED_VERSION = SCS_TELEMETRY_EUT2_GAME_VERSION_CURRENT;
		if (SCS_GET_MAJOR_VERSION(params->common.game_version) > SCS_GET_MAJOR_VERSION(IMPLEMENTED_VERSION)) {
		    params->common.log(SCS_LOG_TYPE_error, "Incompatible (old) version of the telemetry SDK. Please update the SDK.");
			return false;
		}
	}

	if (string(SCS_GAME_ID_ATS) == params->common.game_id) {
		const scs_u32_t MINIMAL_VERSION = SCS_TELEMETRY_ATS_GAME_VERSION_1_00;
		if (params->common.game_version < MINIMAL_VERSION) {
			params->common.log(SCS_LOG_TYPE_error, "Incompatible (old) version of the game. Please update the game.");
			return false;
		}
		const scs_u32_t IMPLEMENTED_VERSION = SCS_TELEMETRY_ATS_GAME_VERSION_CURRENT;
		if (SCS_GET_MAJOR_VERSION(params->common.game_version) > SCS_GET_MAJOR_VERSION(IMPLEMENTED_VERSION)) {
		    params->common.log(SCS_LOG_TYPE_error, "Incompatible (old) version of the telemetry SDK. Please update the SDK.");
        return false;
		}
	}
	return true;
}


Telemetry* telemetry = NULL;

SCSAPI_RESULT scs_telemetry_init(const scs_u32_t version, const scs_telemetry_init_params_t *const init_params) {
    const scs_telemetry_init_params_v100_t *const params = static_cast<const scs_telemetry_init_params_v100_t *>(init_params);
	if (version != SCS_TELEMETRY_VERSION_1_00) {
		return SCS_RESULT_unsupported;
	}
	if (! Telemetry::compatible_version(params)) {
	    return SCS_RESULT_unsupported;
	}

	telemetry = new Telemetry(params);
	return SCS_RESULT_ok;
}

SCSAPI_VOID scs_telemetry_shutdown(void) {
    delete telemetry;
}
