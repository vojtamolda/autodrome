#include <string>
#include <memory>
#include <exception>

#include <zmq.hpp>

#include <scssdk_telemetry.h>
#include <amtrucks/scssdk_ats.h>
#include <amtrucks/scssdk_telemetry_ats.h>
#include <eurotrucks2/scssdk_eut2.h>
#include <eurotrucks2/scssdk_telemetry_eut2.h>


using namespace std;
using namespace zmq;

class Telemetry {

public:
    Telemetry(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version);
    void configuration(const struct scs_telemetry_configuration_t *const configuration_info);
    void start();
    void frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info);
    void frame_end();
    void pause();
    ~Telemetry();

    static SCSAPI_VOID channel_update(const scs_string_t name, const scs_u32_t index, const scs_value_t *const value, const scs_context_t context);

    static SCSAPI_VOID configuration_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
    static SCSAPI_VOID start_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
    static SCSAPI_VOID frame_start_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
    static SCSAPI_VOID frame_end_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
    static SCSAPI_VOID pause_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);

    void log(const string& message, const scs_log_type_t type=SCS_LOG_TYPE_message);
    bool check_version(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version);

protected:
    bool register_event(const scs_telemetry_init_params_v100_t *const params, const scs_event_t event, const scs_telemetry_event_callback_t callback);
    bool register_channel(const scs_telemetry_init_params_v100_t *const params, const scs_string_t name, const scs_value_type_t type, const scs_context_t context);

    bool paused;
    scs_log_t game_log;
    context_t zmq_context;
    socket_t zmq_publisher;

    struct Packet {
        scs_value_dplacement_t placement;
        scs_value_dvector_t linear_velocity;
        scs_value_dvector_t angular_velocity;
        scs_double_t speed;
        scs_timestamp_t render_time;
        scs_timestamp_t simulation_time;
        scs_timestamp_t paused_simulation_time;
    } packet;

};
